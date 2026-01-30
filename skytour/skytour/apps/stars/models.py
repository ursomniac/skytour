import math, re
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.translation import gettext as _
from jsonfield import JSONField
from skyfield.api import Star
from taggit.managers import TaggableManager

from ..abstract.models import Coordinates, WikipediaPage, WikipediaPageObject, AnnalsDeepSkyAbstract
from ..astro.coords import equ2ecl
from ..dso.utils import create_shown_name
from ..utils.models import Constellation, StarCatalog
from .utils import create_star_name, parse_designation, get_bright_star_sort_key,\
    handle_formatting, handle_parameters
from .values import get_values
from .vocabs import GCVS_ID, VARDES, VARIABLE_CLASSES, UNICODE, SUPERSCRIPT_CHAR,\
    NOTE_CATEGORIES, STAR_FLAGS, FULL_ENTITY


# TODO V2: Come up with a plan to use this
class DoubleStar(Coordinates):
    catalog = models.ForeignKey('utils.StarCatalog', on_delete = models.CASCADE)
    id_in_catalog = models.CharField (
        _('ID'),
        max_length = 24
    )
    shown_name = models.CharField (
        _('Shown Name'),
        max_length = 180,
        null = True, blank = True
    )
    constellation = models.ForeignKey (Constellation, 
        on_delete=models.PROTECT,
        null = True, blank = True
    )
    components = models.CharField (
        _('Components'),
        max_length = 20,
        null = True, blank = True
    )
    separation = models.FloatField(
        _('Ang. Sep'),
        help_text = 'Arcseconds',
        null = True, blank = True
    )
    magnitudes = models.CharField(
        _('Magnitudes'),
        max_length = 100,
        help_text = 'comma separated'
    )
    spectral_type = models.CharField (
        _('Spectral Type'),
        max_length = 100
    )
    notes = models.TextField (
        _('Notes'),
        null = True, blank = True
    )
    distance = models.FloatField (
        _('Distance'),
        null = True, blank = True,
        help_text = 'light years'
    )
    tags = TaggableManager(blank=True)

    @property
    def alias_list(self):
        aliases = []
        for alias in self.aliases.all():
            aliases.append(alias.shown_name)
        return ', '.join(aliases)

    @property
    def get_magnitudes(self):
        str_mags = self.magnitudes.split(',')
        mags = []
        for star in str_mags:
            mags.append(float(star))

    def save(self, *args, **kwargs):
        self.ra = self.ra_float # get from property
        self.dec = self.dec_float # get from property
        self.ra_text = self.format_ra # get from property
        self.dec_text = self.format_dec # get from property
        self.shown_name = create_shown_name(self)
        super(DoubleStar, self).save(*args, **kwargs)

    def __str__(self):
        return f"{self.pk}: ({self.constellation.abbreviation}) = {self.shown_name}"

class DoubleStarAlias(models.Model):
    object = models.ForeignKey(DoubleStar, 
        on_delete=models.CASCADE,
        related_name='aliases'
    )
    catalog = models.ForeignKey('utils.StarCatalog', on_delete = models.CASCADE)
    id_in_catalog = models.CharField (
        _('ID'),
        max_length = 24
    )

class DoubleStarElements(models.Model):
    object = models.OneToOneField (
        DoubleStar,
        on_delete = models.CASCADE,
        null = True, blank = True,
        related_name = 'elements'
    )
    period = models.FloatField (
        _('Orbital Period'),
        help_text = 'years'
    )
    periastron = models.FloatField (
        _('Periastron Passage'),
        help_text = 'year'
    )
    semimajor_axis = models.FloatField (
        _('Semi-Major Axis'),
        help_text = 'arcsec'
    )
    eccentricity = models.FloatField (
        _('Eccentricity')
    )
    inclination = models.FloatField (
        _('Inclination'),
        help_text = 'degrees'
    )
    ascending_node = models.FloatField (
        _('Ascending Node'),
        help_text = 'degrees'
    )
    argument = models.FloatField (
        _('Argument of Periastron'),
        help_text = 'degrees'
    )

    @property
    def _p(self):
        return self.period
    @property
    def _t(self):
        return self.periastron
    @property
    def _a(self):
        return self.semimajor_axis
    @property
    def _e(self):
        return self.eccentricity
    @property
    def _i(self):
        return self.inclination
    @property
    def _ir(self):
        return math.radians(self.inclination)
    @property
    def _om(self):
        return self.ascending_node
    @property
    def _omr(self):
        return math.radians(self.ascending_node)
    @property
    def _ap(self):
        return self.argument
    @property
    def _apr(self):
        return math.radians(self.argument)


    def __str__(self):
        return f"{self.pk}: {self.object}"

class BrightStarMetadata(models.Model):
    star = models.OneToOneField(
        'BrightStar', 
        on_delete = models.CASCADE,
        primary_key = True,
        related_name='metadata'
    )
    # For MOST BSC stars this is a dict
    # For 30 stars this will be a list of dicts...!
    metadata = models.JSONField(
        null=True, blank=True,
        help_text='JSON object constructed from SIMBAD lookup'
    )

class BrightStar(Coordinates, WikipediaPageObject):
    """
    Bright Star Catalog data
    """
    # IDS
    hr_id = models.PositiveIntegerField(_('HR #'))
    bayer = models.CharField(_('Bayer'), max_length=10, null=True, blank=True)
    flamsteed = models.CharField(_('Flamsteed'), max_length=10, null=True, blank=True)
    constellation = models.ForeignKey(Constellation, on_delete=models.CASCADE, null=True, blank=True)
    bd_id = models.CharField(_('BD #'), max_length=11, null = True, blank = True)
    hd_id = models.PositiveIntegerField( _('HD #') ,  null=True, blank=True)
    sao_id = models.PositiveIntegerField(_ ('SAO #'), null=True, blank=True)
    fk5_id = models.PositiveIntegerField( _('FK5 #'), null=True, blank=True)
    double_star = models.CharField(_('Double Star Code'), max_length=1, blank=True, null=True)
    ads_id = models.CharField(_('ADS Designation'), max_length=5, null=True, blank=True)
    var_id = models.CharField(_('Var. Star ID'), max_length=9, null=True, blank=True)
    # COORDS
    gal_long = models.FloatField(_('Gal. Long.'), blank=True, null=True)
    gal_lat = models.FloatField(_('Gal. Lat.'), null=True, blank=True)
    # MAG/COLOR
    magnitude = models.FloatField(_('V Mag.'), blank=True, null=True)
    b_v = models.FloatField(_('B-V'), null=True, blank=True)
    u_b = models.FloatField(_('U-B'), null=True, blank=True)
    r_i = models.FloatField(_('R-I'), null=True, blank=True)
    # SPECTRAL TYPE
    spectral_type = models.CharField(_('Spectral Type'), max_length=20, null=True, blank=True)
    spt_code = models.CharField(_('Sp. Type Code'), max_length=1, null=True, blank=True)
    # PROPER MOTION
    pm_ra = models.FloatField(_('Prop. Motion RA'), null=True, blank=True)
    pm_dec = models.FloatField(_('Prop. Motion Dec.'), null=True, blank=True)
    # PARALLAX
    parallax_flag = models.CharField(_('Parallax Flag'), max_length=1, null=True, blank=True)
    parallax = models.FloatField(_('Parallax'), null=True, blank=True)
    # RADIAL VELOCITY
    radial_velocity = models.FloatField(_('Radial Velocity'), null=True, blank=True)
    rv_flag = models.CharField(_('RV Flag'), max_length=1, null=True, blank=True)
    # ROTATION
    rot_flag = models.CharField(_('Rot. Vel. Flag'), max_length=2, null=True, blank=True)
    vsini = models.PositiveIntegerField(_('v sin i'), null=True, blank=True)
    # DOUBLE STAR
    d_mag = models.FloatField(_('d Mag (double)'), null=True, blank=True)
    ang_sep = models.FloatField(_('Ang. Sep.'), null=True, blank=True)
    ads_components = models.CharField(_('Components'), max_length=2, null=True, blank=True)

    ### ADDED FIELDS
    note_flag = models.BooleanField(_('Notes'), default=False)
    name = models.CharField(_('Name'), max_length=40, null=True, blank=True )
    proper_name = models.CharField(_('Proper Name'), max_length=100, null=True, blank=True)
    name_explanation = models.TextField(_('Name Explanation'), null=True, blank=True)
    other_bayer = models.CharField(_('Other Bayer'), max_length=8, null=True, blank=True)
    other_constellation_name = models.CharField(_('Other Constellation Name'),
            max_length=20, null=True, blank=True,
            help_text = 'For stars that changed constellations when the IAU set boundaries'
    )
    tags = TaggableManager(blank=True)

    @property
    def skyfield_object(self):
        return Star(ra_hours=self.ra_float, dec_degrees=self.dec_float)
    
    @property
    def hr_name(self):
        return f"HR {self.hr_id}" if self.hr_id else None
    
    @property
    def hd_name(self):
        return f"HD {self.hd_id}" if self.hd_id else None
    
    @property
    def title_name(self):
        names = (
            self.proper_name,
            self.printable_name,
            self.hr_name,
            self.hd_name
        )
        for n in names:
            if n is not None and n.strip() != '':
                return n
        return '???' # shouldn't get here

    @property
    def plot_label(self):
        if not self.name:
            return None
        first = self.name.split(' ')[0]
        if first.isdecimal():
            return first
        # else it has a letter or a greek letter and possibly a number
        return parse_designation(first)

    @property
    def printable_name(self, hd=True):

        def fix_bayer(x):
            pieces = x.split()
            s = pieces[0]
            if len(pieces) > 1 and pieces[1].isdigit():
                z = int(pieces[1])
                if z < 10 and z > 0:
                    s += SUPERSCRIPT_CHAR[z]
                else:
                    s += pieces[1]
            else:
                return x
            return s
        
        constellation = self.constellation
        name = None
        if self.bayer:
            if self.bayer[-1].isdigit(): # there's a number
                grk = self.bayer[:-1].rstrip()
                num = self.bayer[-1]
                if grk in UNICODE.keys():
                    name = UNICODE[grk] + SUPERSCRIPT_CHAR[int(num)] + " {}".format(constellation.abbr_case)
            if name is None and self.bayer in UNICODE.keys():
                name = UNICODE[self.bayer] + " {}".format(constellation.abbr_case)
            if name is None:
                name = f"{fix_bayer(self.bayer)} {constellation.abbr_case}"
        elif self.flamsteed:
            name = "{} {}".format(self.flamsteed, constellation.abbr_case)
        elif self.var_designation:
            name = self.var_designation
        elif self.other_bayer:
            name = "{} {}".format(fix_bayer(self.other_bayer), constellation.abbr_case)
        #elif self.other_constellation_name:
        #    name = f"({self.other_constellation_name})"
        #else:
        #    name = "HD "+str(self.hd_id)
        return name 
    
    @property
    def name_sort_key(self):
        return get_bright_star_sort_key(self)
    
    @property
    def var_designation(self):
        if self.var_id is None:
            return None
        if self.var_id == self.name:
            return None # already have it
        # PROBLEM: many of these are just a number - which I THINK is the NSV
        #   but so far I can't confirm that.
        # SO: for now just ignore them
        if self.var_id.isnumeric():
            return None
        if self.var_id[:3] == 'Var':
            return None
        return self.var_id    
    
    @property
    def shown(self):
        v = get_values(self)
        return v
    
    @property
    def parallax_flag_str(self):
        if not self.parallax:
            return None
        return 'Dyn.' if self.parallax_flag == 'D' else 'Trig.'
    
    @property
    def double_flag_str(self):
        if self.double_star == 'A':
            return 'Astrometric'
        elif self.double_star == 'D':
            return 'Disc. by occultation'
        elif self.double_star in ['I','R','W']:
            return None # this refer to specific catalogs
        elif self.double_star == 'S':
            return 'Disc. by speckle interferometry'
        return None
    
    @property
    def var_metadata(self):
        if hasattr(self, 'variablestar'):
            return self.variablestar
        return None
    
    @property
    def annals_metadata(self):
        if hasattr(self, 'annals'):
            return self.annals
        return None
    
    @property
    def total_proper_motion(self):
        if self.pm_ra and self.pm_dec:
            total = math.sqrt(self.pm_ra**2 + self.pm_dec**2)
            return total
        return None
    
    @property
    def rv_flag_str(self):
        if self.rv_flag is None:
            return None
        if self.rv_flag == 'V':
            return 'Var.'
        elif self.rv_flag == 'V?':
            return 'Var?'
        elif self.rv_flag[:2] == 'SB':
            return self.rv_flag
        elif self.rv_flag == 'O':
            return 'Orbit'
        return self.rv_flag # catch-all for None or something else
    
    @property
    def distance(self):
        try:
            return self.shown['distance']['ly']['value']
        except:
            return 3.26/self.parallax if self.parallax else None
    
    @property
    def distance_pc(self):
        try:
            return self.shown['distance']['pc']['value']
        except:
            return 1./self.parallax if self.parallax else None
        
    @property
    def absolute_magnitude(self):
        if self.distance_pc and self.magnitude:
            pc = self.distance_pc
            mag = self.magnitude
            amag = mag - 5.*(math.log10(pc)-1.)
            return amag
        return None
    
    @property
    def ecliptic_coordinates(self):
        return equ2ecl(self.ra_float, self.dec_float)
    
    @property
    def format_bd(self):
        x = self.bd_id
        if x is not None:
            if x[-7:].isnumeric(): # when there are >9999 stars
                x = x[:-7] + x[-7:-5] + ' ' + x[-5:]
            if ' ' in x:
                p = x.split()
                return f"{p[0]}°{p[1]}"
        return self.bd_id if self.bd_id else None
        
    @property
    def flags(self):
        ff = []
        # Wiki
        if self.has_wiki == 'WIKI':
            ff.append('W')
        # Variable Star
        if hasattr(self, 'variablestar'):
            ff.append('V')
        # Annals
        if hasattr(self, 'annals'):
            ff.append('A')
        # TODO: DoubleStar
        return ff
    
    @property
    def flags_html(self):
        flags = self.flags
        uni = [STAR_FLAGS[x][2] for x in flags]
        return '&nbsp;&nbsp;'.join(uni)

    @property
    def default_wikipedia_name(self):
        # It appears that Wikipedia is indexed against HR #'s - so for now try that
        # TODO: for Supplement stars, this will prob. need to be HD #
        return f"HR {self.hr_id}"
    
    @property
    def default_wikipedia_star_name(self):
        x = ''
        names = [self.name, self.var_designation]
        name = next((item for item in names if item is not None), None)
        if name is None:
            return None
        # name e.g., 'Pi 3 Ori'
        pieces = name.split(' ')
        id = pieces[0]
        # issues:
        #   Pi3 or Pi 3
        if id in FULL_ENTITY.keys():
            x = FULL_ENTITY[id]
        elif id[0].isalpha() and id[-1].isnumeric():
            if id[:-1] in FULL_ENTITY.keys():
                x = FULL_ENTITY[id[:-1]] + id[-1]
            else:
                x = id # This might handle things like L2 Pup
        else:
            x = id
        if len(pieces) == 3: # Pi 3 Ori
            x += pieces[1]
        # The last one is the constellation
        x += '_'
        g = self.constellation.genitive.replace('ö', 'o')
        x += g.replace(' ','_')
        return x
    
    def get_absolute_url(self):
        """
        Django
        """
        return '/stars/hr/{}'.format(self.pk)
    
    def save(self, *args, **kwargs):
        self.ra = self.ra_float # get from property
        self.dec = self.dec_float # get from property
        self.ra_text = self.format_ra # get from property
        self.dec_text = self.format_dec # get from property
        self.name = create_star_name(self)
        super(BrightStar, self).save(*args, **kwargs)

    def __str__(self):
        hr = f'HR {self.hr_id}'
        hd = f'HD {self.hd_id}' if self.hd_id is not None else None
        name = ' = '.join(filter(None, [hr, hd, self.printable_name, self.var_designation, self.proper_name]))
        return name

class BrightStarWiki(WikipediaPage):
    object = models.OneToOneField(
        BrightStar, 
        on_delete=models.CASCADE,
        primary_key = True,
        related_name = 'wiki'
    )

class BrightStarNotes(models.Model):
    star = models.OneToOneField (
        BrightStar, 
        on_delete = models.CASCADE,
        primary_key = True,
        related_name = 'texts'
    )
    bsc_notes = models.JSONField (
        _('BSC Notes'),
        null = True, blank = True
    )
    description = models.TextField (
        null = True, blank = True
    )
    other_parameters = models.TextField (
        null = True, blank = True
    )

    @property 
    def notes_as_text(self):
        text = ''
        if self.bsc_notes is None:
            return None
        for k, v in self.bsc_notes.items():
            entry = f'{NOTE_CATEGORIES[k]}:\n'
            entry += '\n'.join(v)
            entry += '\n\n'
            text += entry
        return text

    @property
    def notes_as_html(self):
        html = "<div class='bsc_note'>"
        if self.bsc_notes is None:
            return None
        for k, v in self.bsc_notes.items():
            entry = f"<h3 class='bsc_note_header'>{NOTE_CATEGORIES[k]}</h3>"
            text = ' '.join(v)
            entry += f"<p class='bsc_note_entry'>{text}</p>"
            html += entry
        html += '</div>'
        return html
    
    @property
    def other_parameters_text(self):
        ncols = 3
        style = 'other-param-label'
        return handle_parameters(self.other_parameters, ncols, label_style=style)

# TODO V2: Come up with a plan to use this
class VariableStar(Coordinates, WikipediaPageObject):
    catalog = models.ForeignKey(StarCatalog, on_delete=models.CASCADE)
    id_in_catalog = models.CharField(
        _('GCVS ID'),
        max_length = 7,
        null = True, blank = True,
        help_text = "ccnNNNd: cc=const, nNNN is V*# or greek/bayer/flamsteed d is component"
    )
    name = models.CharField(_('Name'), max_length=30)
    slug = models.SlugField(_('Slug'))
    constellation = models.ForeignKey (Constellation, on_delete=models.PROTECT)
    # magnitudes
    mag_code = models.CharField(_('Mag Code'), max_length=2, null=True, blank=True)
    mag_max = models.FloatField(_('Mag Max'), null=True, blank=True)
    mag_max_limit = models.CharField(_('Mag Max Limit'), max_length=1, null=True, blank=True)
    mag_max_uncertainty = models.CharField(_('Mag Max Unc'), max_length=1, null=True, blank=True)
    #
    mag_min1 = models.FloatField('Mag Min 1', null=True, blank=True)
    mag_min1_limit = models.CharField(_('Mag Min 1 Limit'), max_length=1, null=True, blank=True)
    mag_min1_uncertainty = models.CharField(_('Mag Min 1 Unc'), max_length=1, null=True, blank=True)
    mag_min1_system = models.CharField(_('Mag Min 1 System'), max_length=2, null=True, blank=True)
    mag_min1_amplitude = models.FloatField(_('Min 1 Amplitude'), null=True, blank=True)
    #
    mag_min2 = models.FloatField('Mag Min 2', null=True, blank=True)
    mag_min2_limit = models.CharField(_('Mag Min 2 Limit'), max_length=1, null=True, blank=True)
    mag_min2_uncertainty = models.CharField(_('Mag Min 2 Unc'), max_length=1, null=True, blank=True)
    mag_min2_system = models.CharField(_('Mag Min 2 System'), max_length=2, null=True, blank=True)
    mag_min2_amplitude = models.FloatField(_('Min 2 Amplitude'), null=True, blank=True)
    # period, period_type (var, etc.), epoch (for eclipsing vars, etc.)
    period = models.FloatField(_('Period'), null=True, blank=True, help_text='days')
    period_uncertainty = models.CharField(_('Period Unc.'), max_length=5, null=True, blank=True)
    # var_type
    type_original = models.CharField (_('Type'), max_length=10, null=True, blank=True)
    type_revised = models.CharField(_('New Type'), max_length=10, null=True, blank=True)
    # light_curve_image
    # finding_chart (pref with comparison star mags)
    # spectral_type, color_indexes
    spectral_type = models.CharField(_('Spectral Type'), max_length=20, null=True, blank=True)
    # GCVS / NSV
    # catalog designations: Bayer/Flamsteed, V*, HD, SAO, BD, HR
    #   - set one alias as "canonical" = V*, unless NSV
    # common name (e.g., Algol)
    # Bright Star 1:1 - can overlap with it.
    bsc_id = models.OneToOneField(BrightStar, on_delete=models.PROTECT, null=True, blank=True)
    # Aliases - M:1 ForeignKey
    # Notes
    tags = TaggableManager(blank=True)

    # TODO: for lookups of stars here that are in the Annals but NOT in the BSC
    # e.g., this will work...
    # zz = VariableStar.objects.filter(constellation__abbreviation='AND', bsc_id__isnull=True, annals__isnull=False)

    ### USE http://www.sai.msu.su/gcvs/gcvs/gcvs5/htm/ as a guide!
    def get_absolute_url(self):
        return '/variable_star/{}'.format(self.id_in_catalog)

    def __str__(self):
        return f"{self.pk}: {self.name} ({self.type_original})"

    def save(self, *args, **kwargs):
        self.ra = self.ra_float # get from property
        self.dec = self.dec_float # get from property
        self.ra_text = self.format_ra # get from property
        self.dec_text = self.format_dec # get from property
        super(VariableStar, self).save(*args, **kwargs)

    def deconstruct_gcvs(self, greek=True):
        gcvs = self.id_in_catalog
        const_id = int(gcvs[:2])
        constellation = Constellation.objects.get(pk=const_id)
        if gcvs[2] == '9':
            id_in_const = GCVS_ID[gcvs[2:6]] if greek else GCVS_ID[gcvs[2:6]]
        else:
            raw = int(gcvs[2:6])
            if raw > 334:
                id_in_const = f"V{raw}"
            else:
                id_in_const = VARDES[raw]
            
        component = gcvs[-1] if len(gcvs) == 7 else ''
        if component.isdigit():
            number = component
            component = None
        else:
            number = None
        return(id_in_const, number, constellation.abbr_case, component)
    
    @property
    def name_sort_key(self):
        id = self.id_in_catalog
        pri = {'90': 1, '91': 2, '92': 3}
        des = id[2:4]
        p = 4 if des not in pri.keys() else pri[des]
        n = '0' if len(id) < 7 else ''
        return f"{p:01d}{id}{n}"

    @property
    def is_observable(self):
        return (hasattr(self, 'observablevariablestar') and self.observablevariablestar is not None)

    @property
    def default_wikipedia_name(self):
        index = self.name.split()[0]
        if index[:2] == 'V0':
            index = f"V{index[2:]}"
        genitive = self.constellation.genitive
        return f"{self.index}_{genitive}"
    
    @property
    def printable_name(self):
        if self.name == 'V0':
            return 'V'+self.name[2:]
        return self.name
    
    @property
    def html_name(self):
        id_in_const, number, const, comp = self.deconstruct_gcvs()
        x = id_in_const
        if number is not None:
            x += f"<sup>{number}</sup>"
        x += f" {const}"
        if comp is not None:
            x += f" {comp}"
        return x
    
    @property
    def is_active(self):
        return hasattr(self, 'observablevariablestar')
    
    @property
    def mag_range(self):
        return f"{self.mag_max} - {self.mag_min1}"
    
    @property
    def type_original_metadata(self):
        x = VariableStarTypeOriginal.objects.filter(code=self.type_original).first()
        return x

    def get_all_original_types(self):
        x = self.type_original
        return re.split(r"[+|/]", x.replace(':','')) if x is not None else []

    def get_all_revised_types(self):
        x = self.type_revised
        return re.split(r"[+|/]", x.replace(':','')) if x is not None else []

    def info(self):
        print(f"""
            Name: {self.name}
            Aliases: {self.aliases.all()}

        """)

class AbstractVariableStarType(models.Model):
    code = models.CharField (
        _('Code'),
        max_length = 16,
        unique = True
    )
    type_class = models.CharField (
        _('Class'),
        max_length = 100,
        choices = VARIABLE_CLASSES
    )
    name = models.CharField (
        _('Name'),
        max_length = 100,
        null = True, blank = True
    )
    short_description = models.CharField (
        _('Short Description'),
        max_length = 200,
        null = True, blank = True
    )
    notes = models.TextField (
        _('Text'),
        null = True,
        blank = True
    )
    prototype = models.CharField (
        _('Prototype'),
        max_length = 40,
        null = True, blank = True
    )

    def __str__(self):
        return f"{self.pk}: {self.code} = {self.name}"

    class Meta:
        abstract = True
        ordering = ['pk']

class VariableStarTypeOriginal(AbstractVariableStarType):
    pass

class VariableStarTypeRevised(AbstractVariableStarType):
    pass

class VariableStarAlias(models.Model):

    object = models.ForeignKey(VariableStar, 
        on_delete=models.CASCADE,
        related_name='aliases'
    )
    catalog = models.ForeignKey('utils.StarCatalog', on_delete = models.CASCADE)
    id_in_catalog = models.CharField (
        _('ID'),
        max_length = 24
    )
    shown_name = models.CharField (
        _('Shown Name'),
        max_length = 100,
        null = True, blank = True
    )
    class Meta:
        verbose_name = 'Variable Star Alias'
        verbose_name_plural = 'Variable Star Aliases'

    def __str__(self):
        return self.shown_name

    def save(self, *args, **kwargs):
        self.shown_name = create_shown_name(self)
        super(VariableStarAlias, self).save(*args, **kwargs)

class VariableStarNotes(models.Model):
    gcvs = models.OneToOneField (
        VariableStar, 
        on_delete = models.CASCADE,
        null = True, blank = True
    )
    notes = models.TextField (
        _('Notes'),
        blank = True, null = True
    )

    @property
    def formatted_notes(self):
        n = self.notes
        pattern = r'\[\d+\]'
    # re.sub replaces all occurrences of the pattern with an empty string
        text = re.sub(pattern, '', n)
        return text.replace('\n', '').replace('\r', '')
    
    def __str__(self):
        return f"{self.gcvs} - Notes"

class ObservableVariableStar(models.Model):
    gcvs = models.OneToOneField (
        VariableStar,
        on_delete = models.CASCADE,
        null = True, blank = True,
        help_text = 'link to GCVS record'
    )
    finder_chart = models.ImageField (
        _('AAVSO Finder Chart'),
        upload_to = 'aavso_finder_chart',
        null = True, blank = True,
        help_text = 'AAVSO Finder Chart'
    )
    finder_chart_mag = models.FloatField (
        _('Finder Limiting Mag'),
        default = 14.5
    )
    finder_chart_fov = models.FloatField (
        _('Finder Char FOV'),
        default = 60.,
        help_text = '(arcmin)'
    )
    finder_json = JSONField (
        _('Finder JSON'),
        null = True, blank = True
    )

    @property
    def comparison_star_list(self):
        #
        def handle_coordinates(x, type):
            pieces = x.split(':')
            if pieces[0][0] != '-': # N add +
                pieces[0] = '+' + pieces[0]
            return f"{pieces[0]}h{pieces[1]}m{pieces[2]}s" if type == 'ra'\
                else f"{pieces[0]}°{pieces[1]}\'{pieces[2]}\""
        #
        def assemble_mags(bands):
            x = {}
            for b in bands:
                if b['error']:
                    z = f"{b['mag']:6.3f} ± {b['error']:5.3f}"
                else:
                    z = f"{b['mag']:6.3f}"
                x[b['band']] = (b['mag'], z)
            return x
        #
        def get_best_mag(mags):
            precedence = ['V', 'B', 'Rc', 'R', 'I', 'Ic', 'K', 'H', 'U']
            for p in precedence:
                if p in mags.keys():
                    t = tuple(list(mags[p]) + [p])
                    return t
        #
        clist = []
        if not self.finder_json:
            return None
        cc = self.finder_json['photometry']
        for c in cc:
            mags = assemble_mags(c['bands']) # dict of tuples
            best_mag = get_best_mag(mags) # tuple
            x = dict(
                id = c['auid'],
                ra = handle_coordinates(c['ra'], type='ra'),
                dec = handle_coordinates(c['dec'], type='dec'),
                label = c['label'],     
                mags = mags,
                best_mag = best_mag        
            )
            clist.append(x)
        return clist

    def __str__(self):
        return self.gcvs.name
    
    class Meta:
        ordering = ['gcvs__id_in_catalog']
    
class VariableStarLightCurve (models.Model):
    parent = models.ForeignKey(
        VariableStar,
        on_delete = models.CASCADE,
        null = True, blank = True
    )
    image_file = models.ImageField (
        _('Image Field'),
        upload_to = 'variable_star_light_curves',
    )
    order_by = models.PositiveIntegerField (
        _('Order in List'),
        default = 10
    )
    date_start = models.DateField (
        _('Date Start'),
        null = True, blank = True
    )
    date_end = models.DateField (
        _('Date End'),
        null = True, blank = True
    )

    def __str__(self):
        return f"{self.parent}"
    
class VariableStarWiki(WikipediaPage):
    object = models.OneToOneField(
        VariableStar, 
        on_delete=models.CASCADE,
        primary_key = True,
        related_name = 'wiki'
    )

class StellarObject(Coordinates, WikipediaPageObject):
    """
    This is for stars that don't fit into the BrightStar, DoubleStar, or VariableStar models.
    """
    pass
    # mag, colors, notes
    constellation = models.ForeignKey (Constellation, on_delete=models.PROTECT)
    catalog = models.ForeignKey (StarCatalog, on_delete=models.PROTECT)
    proper_name = models.CharField (
        max_length = 40,
        null = True, blank = True
    )
    id_in_catalog = models.CharField (
        _('ID'),
        max_length = 24
    )
    name = models.CharField (
        _('Name'),
        max_length = 180,
        null = True, blank = True
    )
    magnitude = models.FloatField (
        _('Magnitude'),
        blank = True, null = True
    )
    spectral_type = models.CharField (
        _('Spectral Type'),
        max_length = 100
    )
    notes = models.TextField (
        _('Notes'),
        null = True, blank = True
    )
    other_parameters = models.TextField (
        _('Other Params'),
        null = True, blank = True,
        help_text = "Age, etc., in x: y; format - see README"
    )
    distance = models.FloatField (
        _('Distance'),
        null = True, blank = True,
        help_text = 'light years'
    )
    tags = TaggableManager(blank=True)

    # Catalogs
    # Aliases
    #

    @property
    def shown_name(self):
        return f"{self.catalog.abbreviation} {self.id_in_catalog}"
    
    def __str__(self):
        return self.shown_name

    def save(self, *args, **kwargs):
        self.ra = self.ra_float # get from property
        self.dec = self.dec_float # get from property
        self.ra_text = self.format_ra # get from property
        self.dec_text = self.format_dec # get from property
        super(StellarObject, self).save(*args, **kwargs)

class StellarObjectMetadata(models.Model):
    star = models.OneToOneField(
        StellarObject, 
        on_delete=models.CASCADE, 
        primary_key=True,
        related_name = 'metadata'
    )
    simbad_lookup = models.CharField(
        max_length=20,
        null = True, blank = True
    )
    metadata = models.JSONField(
        null=True, blank=True,
        help_text='JSON object constructed from SIMBAD lookup'
    )
class StellarObjectWiki(WikipediaPage):
    object = models.OneToOneField(
        StellarObject, 
        on_delete=models.CASCADE,
        primary_key = True,
        related_name = 'wiki'
    )

class AnnalsDeepSkyStar(AnnalsDeepSkyAbstract):
    bright_star = models.OneToOneField (
        BrightStar,
        null = True, blank = True,
        on_delete=models.CASCADE,
        related_name = 'annals'
    )
    variable_star = models.OneToOneField (
        VariableStar,
        null = True, blank = True,
        on_delete = models.CASCADE,
        related_name = 'annals'
    )
    double_star = models.OneToOneField (
        DoubleStar,
        null = True, blank = True,
        on_delete = models.CASCADE,
        related_name = 'annals'
    )
    other_star = models.OneToOneField (
        StellarObject,
        null = True, blank = True,
        on_delete = models.CASCADE,
        related_name = 'annals'
    )

    @property
    def constellation(self):
        if hasattr(self, 'bright_star') and self.bright_star is not None:
            return self.bright_star.constellation
        if hasattr(self, 'variable_star') and self.variable_star is not None:
            return self.variable_star.constellation
        if hasattr(self, 'double_star') and self.double_star is not None:
            return self.double_star.constellation
        if hasattr(self, 'other_star') and self.other_star is not None:
            return self.other_star.constellation
        return None
    
    @property
    def flags_list(self):
        s = []
        if hasattr(self, 'bright_star') and self.bright_star is not None:
            s.append('B')
        if hasattr(self, 'variable_star') and self.variable_star is not None:
            s.append('V')
        if hasattr(self, 'double_star') and self.double_star is not None:
            s.append('D')
        if hasattr(self, 'other_star') and self.other_star is not None:
            s.append('O')
        if len(s) == 0:
            return None
        return s
    
    @property
    def flags_str(self):
        ff = self.flags_list
        if ff is None:
            return None
        #s = [STAR_FLAGS[f][2] for f in ff]
        return ", ".join(ff)

    @property
    def refs(self):    
        s = []
        bs = hasattr(self, 'bright_star') and self.bright_star is not None
        vs = hasattr(self, 'variable_star') and self.variable_star is not None
        ds = hasattr(self, 'double_star') and self.double_star is not None
        os = hasattr(self, 'other_star') and self.other_star is not None
        if bs:
            x = self.bright_star
            s.append(f"{x.printable_name} = HR {x.hr_id}")
        if vs:
            v = self.variable_star
            s.append(f"{v.name}")
        if ds:
            d = self.double_star
            s.append(f"{d.name}")
        if os:
            o = self.other_star
            s.append(f"{o.shown_name}")
        return ' = '.join(s)
    
    @property
    def format_notes(self):
        return handle_formatting(self.notes )
    
    def __str__(self):
        return self.refs

@receiver(post_save, sender=BrightStar)
def create_or_update_bright_star_metadata(sender, instance, created, **kwargs):
    if created:
        # Create the RelatedProfile instance only if the ParentModel instance was newly created
        BrightStarMetadata.objects.create(star=instance)
        BrightStarWiki.objects.create(object=instance)
        BrightStarNotes.objects.create(star=instance)
    # Optional: add logic here to update the RelatedProfile if the ParentModel is being updated
    # else:
    #     instance.relatedprofile.save() 

@receiver(post_save, sender=StellarObject)
def create_or_update_stellar_object_metadata(sender, instance, created, **kwargs):
    if created:
        # Create the RelatedProfile instance only if the ParentModel instance was newly created
        StellarObjectMetadata.objects.create(star=instance)
        StellarObjectWiki.objects.create(object=instance)
    # Optional: add logic here to update the RelatedProfile if the ParentModel is being updated
    # else:
    #     instance.relatedprofile.save() 

