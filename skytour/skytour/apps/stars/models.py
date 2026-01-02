import math, re
from django.db import models
from django.utils.safestring import mark_safe
from django.utils.translation import gettext as _
from jsonfield import JSONField
from skyfield.api import Star
from taggit.managers import TaggableManager

from ..abstract.models import Coordinates, WikipediaPage, WikipediaPageObject

from ..dso.utils import create_shown_name
from ..utils.models import Constellation, StarCatalog
from .utils import create_star_name, parse_designation
from .vocabs import ENTITY, GCVS_ID, VARDES, BAYER_INDEX, VARIABLE_CLASSES, GCVS_NO_GREEK


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

class BrightStar(Coordinates, WikipediaPageObject):
    """
    Bright Star Catalog data
    """
    hr_id = models.PositiveIntegerField(_('HR #'))
    bayer = models.CharField(_('Bayer'), max_length=10, null=True, blank=True)
    flamsteed = models.CharField(_('Flamsteed'), max_length=10, null=True, blank=True)
    constellation = models.CharField(_('Constellation'), 
        max_length = 3,
        null = True, blank = True
    )
    bd_id = models.CharField(_('BD #'), max_length=11, null = True, blank = True)
    hd_id = models.PositiveIntegerField( _('HD #') ,  null=True, blank=True)
    sao_id = models.PositiveIntegerField(_ ('SAO #'), null=True, blank=True)
    fk5_id = models.PositiveIntegerField( _('FK5 #'), null=True, blank=True)
    double_star = models.CharField(_('Double Star Code'), max_length=1, blank=True, null=True)
    ads_id = models.CharField(_('ADS Designation'), max_length=5, null=True, blank=True)
    var_id = models.CharField(_('Var. Star ID'), max_length=9, null=True, blank=True)
    # ra_h, ra_m, ra_s, dec_sign, dec_d, dec_m, dec_s in Coordinate abstract class 
    gal_long = models.FloatField(_('Gal. Long.'), blank=True, null=True)
    gal_lat = models.FloatField(_('Gal. Lat.'), null=True, blank=True)
    magnitude = models.FloatField(_('V Mag.'), blank=True, null=True)
    b_v = models.FloatField(_('B-V'), null=True, blank=True)
    u_b = models.FloatField(_('U-B'), null=True, blank=True)
    r_i = models.FloatField(_('R-I'), null=True, blank=True)
    spectral_type = models.CharField(_('Spectral Type'), max_length=20, null=True, blank=True)
    spt_code = models.CharField(_('Sp. Type Code'), max_length=1, null=True, blank=True)
    pm_ra = models.FloatField(_('Prop. Motion RA'), null=True, blank=True)
    pm_dec = models.FloatField(_('Prop. Motion Dec.'), null=True, blank=True)
    parallax_flag = models.CharField(_('Parallax Flag'), max_length=1, null=True, blank=True)
    parallax = models.FloatField(_('Parallax'), null=True, blank=True)
    radial_velocity = models.FloatField(_('Radial Velocity'), null=True, blank=True)
    rv_flag = models.CharField(_('RV Flag'), max_length=1, null=True, blank=True)
    rot_flag = models.CharField(_('Rot. Vel. Flag'), max_length=2, null=True, blank=True)
    vsini = models.PositiveIntegerField(_('v sin i'), null=True, blank=True)
    d_mag = models.FloatField(_('d Mag (double)'), null=True, blank=True)
    ang_sep = models.FloatField(_('Ang. Sep.'), null=True, blank=True)
    notes = models.BooleanField(_('Notes'), default=False)

    name = models.CharField(_('Name'), max_length=40, null=True, blank=True )
    proper_name = models.CharField(_('Proper Name'), max_length=100, null=True, blank=True)
    name_explanation = models.TextField(_('Name Explanation'), null=True, blank=True)
    tags = TaggableManager(blank=True)

    @property
    def skyfield_object(self):
        return Star(ra_hours=self.ra_float, dec_degrees=self.dec_float)

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
    def printable_name(self):
        constellation = self.constellation
        if self.bayer:
            if self.bayer[-1].isdigit(): # there's a number
                grk = self.bayer[:-1].rstrip()
                num = self.bayer[-1]
                name = ENTITY[grk] + "<sup>{}</sup>".format(num) + " {}".format(constellation)
            else:
                name = ENTITY[self.bayer] + " {}".format(constellation)

        elif self.flamsteed:
            name = "{} {}".format(self.flamsteed, constellation)
        else:
            name = "HD "+str(self.hd_id)
        return mark_safe(name)
    
    @property
    def name_sort_key(self):
        """
        Return a coded key such that:
            1. Stars with Greek letters come first in Greek order
            2. Stars with superscripts for a given Greek letter are ordered
            3. Stars with a Flamsteed number and no Greek letter are next
            4. Stars with HD numbers come last
        """
        out = None
        if self.bayer:
            p = 1
            if self.bayer[-1].isdigit(): # there's a number
                x = self.bayer[:-1].rstrip()
                d = self.bayer[-1]
                num = int(d) if d.isdigit() else 0
            else:
                x = self.bayer
                num = 0
            if x in BAYER_INDEX:
                grk = BAYER_INDEX.index(x)
                out = f"{p}{grk:05d}{num:03d}"
            
        if out is None and self.flamsteed:
            p = 2
            num = self.flamsteed
            if num.isdigit():
                out = f"{p}{int(num):08d}"
        if out is None:
            p = 3
            hd = self.hd
            out = f"{p}{out:08d}"
        return out

    @property
    def default_wikipedia_name(self):
        # It appears that Wikipedia is indexed against HR #'s - so for now try that
        return f"HR {self.hr_id}"
    
    def save(self, *args, **kwargs):
        self.ra = self.ra_float # get from property
        self.dec = self.dec_float # get from property
        self.ra_text = self.format_ra # get from property
        self.dec_text = self.format_dec # get from property
        self.name = create_star_name(self)
        super(BrightStar, self).save(*args, **kwargs)

    def __str__(self):
        name = self.printable_name
        if self.proper_name:
            name += " = {}".format(self.proper_name)
        return mark_safe("HR {} = {}".format(self.hr_id, name))

class BrightStarWiki(WikipediaPage):
    object = models.OneToOneField(
        BrightStar, 
        on_delete=models.CASCADE,
        primary_key = True,
        related_name = 'wiki'
    )


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
    def default_wikipedia_name(self):
        index = self.name.split()[0]
        if index[:2] == 'V0':
            index = f"V{index[2:]}"
        genitive = self.name.constellation.genitive
        return f"{self.index}_{genitive}"
    
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

    
class StellarObject(Coordinates):
    """
    This is for stars that don't fit into the BrightStar, DoubleStar, or VariableStar models.
    """
    pass
    # mag, colors, notes
    constellation = models.ForeignKey (Constellation, on_delete=models.PROTECT)
    catalog = models.ForeignKey (StarCatalog, on_delete=models.PROTECT)

    def save(self, *args, **kwargs):
        self.ra = self.ra_float # get from property
        self.dec = self.dec_float # get from property
        self.ra_text = self.format_ra # get from property
        self.dec_text = self.format_dec # get from property
        self.name = create_star_name(self)
        super(StellarObject, self).save(*args, **kwargs)

        