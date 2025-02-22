import datetime as dt
from collections import OrderedDict
from django.db import models
from django.db.models import Avg
from django.utils.html import mark_safe
from django.utils.translation import gettext as _
from jsonfield import JSONField
from skyfield.api import Star
from taggit.managers import TaggableManager
from .utils import create_shown_name
from .vocabs import DISTANCE_UNIT_CHOICES
from ..abstract.models import Coordinates, LibraryAbstractImage, FieldView, ObservingLog, ObservableObject
from ..abstract.utils import get_metadata
from ..abstract.vocabs import YES, NO, YES_NO as INT_YES_NO
from ..astro.angdist import get_neighbors
from ..astro.astro import get_delta_hour_for_altitude
from ..astro.culmination import get_opposition_date
from ..astro.transform import get_alt_az
from ..astro.utils import alt_get_small_sep, get_simple_position_angle, get_atlas_sep
from ..site_parameter.helpers import find_site_parameter
from ..solar_system.utils import get_constellation
from ..utils.models import Constellation, ObjectType
#from .pdf import create_pdf_page
from .observing import get_max_altitude
from .utils import get_hyperleda_value, get_simbad_value
from .vocabs import (
    MODE_PRIORITY_CHOICES,
    MODE_VIABILITY_CHOICES,
    OBSERVING_MODE_TYPES,
    PRIORITY_CHOICES, 
    PRIORITY_COLORS,
    VIABILITY_BACKGROUND_COLORS as VBC,
    VIABILITY_FOREGROUND_COLORS as VFC
)

class DSOAbstract(Coordinates):
    """
    Abstract model covering DSO and DSOInField
    """
    catalog = models.ForeignKey('utils.Catalog', on_delete = models.CASCADE)
    id_in_catalog = models.CharField (
        _('ID'),
        max_length = 24
    )
    shown_name = models.CharField (
        _('Shown Name'),
        max_length = 100,
        null = True, blank = True,
        help_text = 'Override if you want to use a specific designation'
    )
    nickname = models.CharField(
        _('Nickname'),
        max_length = 200,
        null = True, blank = True,
        help_text = 'A nickname, e.g. "Crab Nebula"'
    )
    constellation = models.ForeignKey (Constellation, on_delete=models.PROTECT)
    object_type = models.ForeignKey(ObjectType, on_delete=models.PROTECT)
    morphological_type = models.CharField (
        _('Morphological Type'),
        max_length = 20,
        null = True, blank = True,
        help_text = 'Gal Type, GC Class, etc.'
    )
    magnitude = models.FloatField (
        _('Mag.'),
        null = True, blank = True
    )
    magnitude_system = models.CharField (
        _('Mag. System'),
        max_length = 3, # default = 'V',
        null = True, blank = True,
        help_text = 'e.g., V, B, Phot.'
    )
    angular_size = models.CharField (
        _('Angular Size'),
        max_length = 50,
        null = True, blank = True,
        help_text = 'single or double dimension, e.g., 36\" or  8\'x5\''
    )
    surface_brightness = models.FloatField (
        _('Surface Brightness'),
        null = True, blank = True,
        help_text = 'Mag/arcmin^2 (SQM)'
    )
    contrast_index = models.FloatField (
        _('Contrast Index'),
        null = True, blank = True
    )
    distance = models.FloatField (
        _('Distance'),
        null = True, blank = True,
    )
    distance_units = models.CharField (
        _('Distance Unit'),
        max_length = 10,
        choices = DISTANCE_UNIT_CHOICES,
        null = True, blank = True
    )
    other_parameters = models.TextField (
        _('Other Params'),
        null = True, blank = True,
        help_text = "Age, etc., in x: y; format - see README"
    )
    notes = models.TextField (
        _('Notes'),
        null = True, blank = True
    )
    # From Stellarium DSO model and SIMBAD
    orientation_angle = models.PositiveIntegerField (
        _('Orientation Angle'),
        null = True, blank = True,
        help_text = 'Degrees'
    )
    major_axis_size = models.FloatField (
        _('Size: Major Axis'),
        null = True, blank = True,
        help_text = 'arcmin'
    )
    minor_axis_size = models.FloatField (
        _('Size: Minor Axis'),
        null = True, blank = True,
        help_text = 'arcmin'
    )
    metadata = JSONField(
        null=True, blank=True,
        help_text='JSON object constructed from HyperLeda lookup'
    )
    simbad = JSONField(
        null=True, 
        blank=True,
        help_text='JSON object constructed from SIMBAD lookup'
    )
    override_metadata = JSONField(
        null=True, blank=True,
        help_text='Custom JSON Objects - overrides SIMBAD/HyperLeda values'
    )

    hyperleda_name = models.CharField (
        _('HyperLeda Name Override'),
        max_length = 30,
        null = True, blank = True,
        help_text = 'Use this designation when querying HyperLeda'
    )
    simbad_name = models.CharField (
        _('SIMBAD Name Override'),
        max_length = 30,
        null = True, blank = True,
        help_text = 'Use this designation when querying SIMBAD'
    )

    @property
    def skyfield_object(self):
        """
        This is handy when pointing at this DSO
        """
        return Star(ra_hours=self.ra_float, dec_degrees=self.dec_float)
    
    @property
    def find_magnitude(self):
        """
        Get Magnitude from Hyperleda/Simbad/Override.
        """
        mag = self.magnitude
        hv = get_hyperleda_value(self, 'magnitude')
        sv = get_simbad_value(self, 'magnitude')
        # TODO: Add Override
        if hv is not None:
            return (hv['value'], hv['system'], 'H')
        if sv is not None:
            return (sv['value'], sv['system'], 'S')
        return (mag, None, 'O')
    
    @property
    def find_surface_brightness(self):
        """
        Get Surface Brightness from Hyperleda/Simbad/Override.
        """
        sb = self.surface_brightness
        hv = get_hyperleda_value(self, 'surface_brightness')
        if hv is not None: # Simbad data doesn't have this
            return (hv['value'], 'H')
        return (sb, 'O')
    
    @property
    def find_angular_size(self):
        """
        Get Angular Size from Hyperleda/Simbad/Override.
        """
        size = self.angular_size
        hv = get_hyperleda_value(self, 'angsize')
        sv = get_simbad_value(self, 'angsize')
        # hv or sv or size might work
        if hv is not None:
            return (hv, 'H')
        if sv is not None:
            return (sv, 'S')
        return (size, 'O')
    
    @property
    def find_major_axis_size(self):
        """
        Get Major Axis Size from Hyperleda/Simbad/Override.
        """
        size = self.major_axis_size
        hv = get_hyperleda_value(self, 'amajor')
        sv = get_simbad_value(self, 'amajor')
        if hv is not None:
            return (hv['value'], 'H')
        if sv is not None:
            return (sv['value'], 'S')
        return (size, 'O')
    
    @property
    def find_orientation(self):
        """
        Get Orientation (rotation) from Hyperleda/Simbad/Override
        """
        o = self.orientation_angle
        hv = get_hyperleda_value(self, 'orientation')
        sv = get_simbad_value(self, 'orientation')
        if hv is not None:
            return (hv['value'], 'H')
        if sv is not None:
            return (sv['value'], 'S')
        return (o, 'O')
    
    @property
    def find_distance(self):
        """
        Get Distance from Hyperleda/Simbad/Override
        """
        d = self.distance
        u = self.distance_units
        hv = get_hyperleda_value(self, 'distance')
        sv = get_simbad_value(self, 'distance')

        if hv is not None :
            return hv['value'], hv['units'], 'H'
        if sv is not None:
            return sv['value'], sv['units'], 'S'
        return (d, u, 'O')
    
    @property
    def other_metadata_text(self):
        """
        Get/Format Additional Metadata text
        """
        orig = self.other_parameters
        if orig is not None and orig.strip() != '':
            interim = []
            first = orig.split(';')
            for item in first:
                if item is None or item.strip() == '':
                    continue
                if ':' in item:
                    (label, value) = item.split(':')
                else: # this shouldn't happen but...
                    label = item
                    value = None
                t = tuple((label.strip(), value.strip()))
                interim.append(t)
            second = sorted(interim, key=lambda x: x[0])
            out = []
            for item in second:
                out.append(f"{item[0]}: {item[1]}")
            return out
    
    class Meta:
        abstract = True

class DSO(DSOAbstract, FieldView, ObservableObject):
    """
    Basically everything we want:
        Name and Aliases
            - botn are in the Object Alias abstract class:
                the primary name is in this model, the other
                is in a FK to this model from DSOAlias.
        Images
        Field View (https://astronomy.tools/calculators/field_of_view/)
    """
    finder_chart = models.ImageField (
        _('Finder Chart'),
        upload_to = 'finder_chart/',
        null = True, blank = True,
        help_text = 'Deprecated: finder charts found on the WWW'
    )
    dso_finder_chart = models.ImageField (
        _('DSO Finder Chart'),
        upload_to = 'dso_finder_chart',
        null = True, blank = True,
        help_text = 'This is a printable color finder chart'
    )
    dso_finder_chart_wide = models.ImageField (
        _('Constructed Finder Chart - Wide'),
        upload_to = 'dso_finder_wide',
        null = True, blank = True,
        help_text='Generated wide-field chart'
    )
    dso_finder_chart_narrow = models.ImageField (
        _('Constructed Finder Chart - Narrow'),
        upload_to = 'dso_finder_narrow',
        null = True, blank = True,
        help_text='Generate narrow-field chart'
    )
    dso_imaging_chart = models.ImageField (
        _('Imaging Chart for eQuinox 2'),
        upload_to = 'dso_imaging_charts',
        null = True, blank = True,
        help_text='Generated field from Stellarium'
    )
    priority = models.CharField (
        _('Priority'),
        max_length = 20,
        choices = PRIORITY_CHOICES,
        null = True, blank = True,
        help_text='DEPRECATED'
    )
    show_on_skymap = models.PositiveIntegerField (
        _('Show on Skymap'),
        default = 0,
        choices = INT_YES_NO,
        help_text='Filter for DSOs on skymap'
    )
    pdf_page = models.FileField (
        _('PDF Page'),
        null = True, blank = True,
        upload_to = 'dso_pdf',
        help_text='PDF file --- deprecated?'
    )
    map_label = models.CharField (
        _('Map Label'),
        max_length = 40,
        null = True, blank = True,
        help_text='Override label used on maps/atlas plates'
    )
    tags = TaggableManager(blank=True)
    object_class = 'dso'
    detail_view = 'dso-detail'

    reimage = models.BooleanField(
        default = False,
        help_text = "Check to override image filtering."
    )

    @property
    def instance_id(self):
        return self.pk

    @property
    def alias_list(self):
        """
        Generate a comma-separated list of aliases.
        TODO V2: Or write a script to populate from SIMBAD/Hyperleda - this might
            be problematic for faint/obscure objects.
        """
        aliases = []
        for alias in self.aliases.all():
            if alias.alias_in_field:
                aliases.append(f"{alias.shown_name} (for {alias.in_field_dso})")
            else:
                aliases.append(alias.shown_name)
        return ', '.join(aliases)

    @property
    def opposition_date(self):
        """
        Return Opposition Date based on RA
        """
        return get_opposition_date(self.ra, next=True)
    
    @property
    def hour_angle_min_alt(self):
        """
        Calculate the Hour Angle when the object reaches a minimum altitude
        NOTE: the minimum is set to be 20° generally, can be 5° or 10° - this
            is only because there are handful of DSOs that are REALLY south
            but still very high priority
        BUG: This doesn't know about the latitude of the cookie!
            Therefore it always will use the default location!
        """
        default_min_altitude = find_site_parameter('minimum-object-altitude', default=10., param_type='float')
        ipri = self.imaging_checklist_priority
        alt = 20.
        delta_days, cos_hh = get_delta_hour_for_altitude(self.dec)
        if delta_days is None:
            alt = 5. if (ipri is not None and ipri > 0) else default_min_altitude
            delta_days, cos_hh = get_delta_hour_for_altitude(self.dec, alt=alt)
        return delta_days, cos_hh, alt
    
    @property
    def observing_date_range(self):
        """
        The date range where the object is >20° (usually - with exceptions) at Midnight
        """
        delta_days, cos_hh, alt = self.hour_angle_min_alt
        if delta_days:
            date_min = self.opposition_date - dt.timedelta(days=round(delta_days))
            date_max = self.opposition_date + dt.timedelta(days=round(delta_days))
            return date_min, date_max, alt
        else:
            return None, None, None

    @property
    def nearby_dsos(self):
        """
        Return DSOs within ???° of object...
        """
        return get_neighbors(self)
    
    @property
    def priority_value(self):
        """
        TODO V2: DEPRECATE?
        """
        dv = {'Highest': 4, 'High': 3, 'Medium': 2, 'Low': 1, 'None': 0}
        if self.priority is None:
            return 0
        return dv[self.priority]

    @property
    def priority_color(self):
        if self.priority:
            return PRIORITY_COLORS[self.priority]
        return '#666'

    @property
    def atlas_plate_list(self):
        """
        Return the list of Atlas Plates this DSO is on.
        NOTE: this is not 100% accurate - sometimes an object might be just off the plate
        """
        pp = []
        for p in self.atlasplate_set.all():
            pp.append(str(p.plate_id))
        return ', '.join(pp)
    
    @property
    def num_library_images(self):
        """
        Return the number of Library Images
        """
        return self.image_library.count()
    
    @property
    def num_slideshow_images(self):
        """
        Return the number of Slideshow Images
        """
        return self.image_library.filter(use_in_carousel=True).count()
    
    # TODO: Add support for multiple telescopes
    @property
    def imaging_checklist_priority(self):
        """
        Return Imaging Checklist Priority
        TODO: DEPRECATE in favor of TargetDSOMode.priority
        """
        c = self.dsoimagingchecklist_set.first()
        if c and c.priority is not None:
            return c.priority
        return None
    
    # TODO: Add support for multiple telescopes
    @property 
    def color_imaging_checklist_priority(self):
        """
        TODO: DEPRECATE in favor of TargetDSOMode.priority
        """
        colors = ['#888', '#c6f', '#6cf', '#0f0', '#ff6', '#f66']
        p = self.imaging_checklist_priority
        if p is not None:
            return colors[p]
        return None
    
    # TODO (someday): Add support for multiple telescopes
    @property
    def library_image_camera(self):
        return '📷' if self.num_library_images > 0 else None
    
    @property
    def library_image_priority(self):
        emoji_numbers = [ 
            u"\u0030\uFE0F\u20E3", # 0
            u"\u0031\uFE0F\u20E3", # 1
            u"\u0032\uFE0F\u20E3", # 2
            u"\u0033\uFE0F\u20E3", # 3
            u"\u0034\uFE0F\u20E3", # 4
            u"\u0035\uFE0F\u20E3"  # 5 
        ]
        light_circle_numbers = [
            u"\u24EA", u"\u2460", u"\u2461", u"\u2462", u"\u2463", u"\u2464"
        ]
        dark_circle_numbers = [
            u"\U0001F10C", u"\u278A", u"\u278B", u"\u278C", u"\u278D", u"\u278E"
        ]
        use = light_circle_numbers

        # TODO: Add support for multiple telescopes
        c = self.dsoimagingchecklist_set.first()
        if c:
            my_priority = c.priority
            if c.priority is not None and c.priority >= 0:
                return use[my_priority]
        # No priority or < 0
        return None
    
    @property
    def library_image(self):
        """
        Return the first (based on order_in_list) image in the Library Image stack.
        """
        return self.image_library.order_by('order_in_list').first() # returns None if none

    @property
    def is_on_imaging_checklist(self):
        """
        Used in HTML pages.
        """
        return self.dsoimagingchecklist_set.count() > 0
    
    @property
    def label_on_chart(self):
        """
        Generate the label for a finding chart or AtlasPlate image.
        Note that DSOs with >0 DSOInField objects get a '+' appended,
        e.g., M33 is shown as M33+ because of the other NGC objects in the FOV.
        """
        in_fov = self.dsoinfield_set.all()
        n_in_fov = in_fov.count()
        label = self.shown_name if self.map_label is None else self.map_label
        if n_in_fov > 0 and self.map_label is None:
            label += '+'
        return label
    
    @property
    def dsos_in_field_count(self):
        """
        Return the number of DSOInField objects associated.
        """
        return self.dsoinfield_set.count()
    
    @property
    def dsoinfield_table(self):
        """
        Generate a table of all the DSOInField objects.
        """
        if self.dsoinfield_set.count() == 0:
            return "None"
    
        out = '<table style="border: 2px solid #666;">'
        out += '<tr style="bgcolor: #333">'
        out += '<th>Name</th><th>Type</th><th>Distance</th>'
        out += '<th>Mag.</th><th>Size</th><th>Surf. Br.</th><th>Admin</th>'
        out += '</tr>'
        fdsos = self.dsoinfield_set.order_by('ra')
        for f in fdsos:
            mag = f"{f.find_magnitude[0]:.2f}" if f.magnitude else ''
            dist = f"{f.primary_distance:.2f}" if f.primary_distance else ''
            pa = f" at {f.primary_angle:.0f}°" if f.primary_angle else ''
            sbr = f"{f.surface_brightness:.2f}" if f.surface_brightness else ''
            size = f.angular_size if f.angular_size else ''
            admin_url = f"/admin/dso/dsoinfield/{f.pk}/change"
            
            out += '<tr>'
            if f.aliases.count() > 0:
                out += f"<td>{ f.name_plus_alias }"
            else:
                out += f"<td>{ f.shown_name }"
            if f.nickname:
                out += f" <span style\"font-size: 80%; font-style: italic; color: #ff6;\">{ f.nickname }</span>"
            out += "</td>"
            out += f"<td>{ f.object_type.short_name }"
            if f.morphological_type:
                out += f" ({ f.morphological_type })"
            out += "</td>"
            out += f"<td>{ dist }\' { pa }</td>"
            out += f"<td>{ mag }</td>"
            out += f"<td>{ size }</td>"
            out += f"<td>{ sbr }</td>"
            out += f"<td><a href='{admin_url}' target='_new'><button>Admin</button></a> {admin_url}</td>"
            out += "</tr>"
        out += "</table>"
        return mark_safe(out)
    
    @property
    def map_image_list(self):
        """
        Generate the list of images for the panel (right-hand side).
        This includes the Stellarium-generated FOV image, plus (usually)
        all of the "landscape" library images.

        TODO: Assign names to each of the panels.
        """
        map_images = self.image_library.filter(use_as_map=True).order_by('order_in_list')
        maps_list = []
        i = 1
        for m in map_images:
            item = {}
            item['url'] = m.image.url
            item['caption'] = ''
            if m.imaging_telescope is not None:
                item['caption'] += f"{m.imaging_telescope}: "
            item['caption'] += f'{m.ut_datetime.strftime("%Y-%m-%d %H:%M")} UT, {m.exposure}min, '
            item['caption'] += f'{m.get_image_style_display()}'
            maps_list.append(item)
            i += 1
        if self.dso_imaging_chart:
            item = {
                'url': self.dso_imaging_chart.url, 
                'caption': f"Finding Chart for eQuinox image."
            }  
            maps_list.append(item)
        return maps_list
    
    @property
    def finder_image_list(self):
        """
        Generate the list of images for the "finder" panel on the DSO page.
        This includes:
            1. The Wide-field map
            2. The Narrow-field map
            3. All the AtlasPlates with the DSO (generally ordered by the proximity to the center)
            4. The printable wide-field chart
            5. Any uploaded 3rd party finder charts (deprecated)
            6. The FOV image from telescope.info (deprecated)
        """
        myra = self.ra
        mydec = self.dec
        finder_images = []
        # Primary field charts
        for chart in [
            self.dso_finder_chart_narrow,
            self.dso_finder_chart_wide,
        ]:
            if chart.name == '':
                continue
            finder_images.append(chart.url)
        # Deal with atlas plates!
        atlas_plates = self.atlasplate_set.all()
        d = {}
        for plate in atlas_plates:
            # 1. get distance from center
            plate_image = plate.atlasplateversion_set.filter(reversed=True, shapes=True).first()
            if plate_image is not None and plate_image.image.url != '':
                mydist = get_atlas_sep(myra, mydec, plate.center_ra, plate.center_dec)
                if mydist > 15.:
                    continue
                d[plate.plate_id] = {
                    'dist': mydist,
                    'url': plate_image.image.url
                }
        od = OrderedDict(sorted(d.items(), key=lambda x: x[1]['dist']))
        for k in od.keys():
            finder_images.append(od[k]['url'])
        # Secondary field charts
        for chart in [
            self.dso_finder_chart,
            self.finder_chart,
            self.field_view
        ]:
            if chart.name == '':
                continue
            finder_images.append(chart.url)
        return finder_images
    
    @property
    def active_observing_list_count(self):
        return self.dsolist_set.filter(active_observing_list=YES).count()
    
    @property
    def is_on_active_observing_list(self):
        return self.active_observing_list_count > 0
    
    @property
    def mode_list(self):
        found = ''
        for my_mode in self.dsoobservingmode_set.all():
            found += my_mode.mode
        return found
    
    @property
    def mode_set(self):
        out = ''
        for k in 'NBSMI':
            out += k if k in self.mode_list else ' '
        return out
    
    def mode_viability_chart(self):
        if self.mode_list == '' or self.mode_list is None:
            return f"No chart."
        out = '<div class="mode-chart">'
        out += '<pre>'
        out += '<span class="mode-header">Mode  Pri  Grid</span><br>'
        for k in 'NBSMI':
            if k not in self.mode_list:
                continue
            mode = self.dsoobservingmode_set.filter(mode=k).first()
            v = mode.viable
            out += f'<b> {k}</b>:  &nbsp;' 
            out += ' 0  &nbsp;' if mode.priority is None else f' {mode.priority}  &nbsp;'
            for i in range(11):
                val = 'X' if i == v else '&nbsp;'
                val = f'&nbsp;{val}&nbsp;'
                span = f"<span style='background-color: {VBC[i]}; color: {VFC[i]}'>"
                span += val + '</span>'
                out += span
            out += f"&nbsp;<span>{mode.get_viable_display():<20s}</span>"
            if mode.interesting:
                out += '<span style="color: #FF0; font-weight: bold;">⚡</span>'
            if mode.challenging:
                out += '<span style="font-size: 75%">🏁</span>'
            out += '<br>'
        out += '</pre></div>'
        return mark_safe(out)
    
    def max_altitude(self, location=None): # no location = default
        """
        Return the maximum altitude a DSO reaches at a given observing location.
        """
        return get_max_altitude(self, location=location)
    
    def finder_chart_tag(self):
        """
        This makes the uploaded finder chart appear on the Admin page.
        """
        return mark_safe(u'<img src="%s" width=500>' % self.finder_chart.url)
    
    def dso_imaging_chart_tag(self):
        return mark_safe(u'<img src="%s" width=500>' % self.dso_imaging_chart.url)

    def dso_finder_chart_narrow_tag(self):
        return mark_safe(u'<img src="%s" width=500>' % self.dso_finder_chart_narrow.url)
    
    def dso_finder_chart_wide_tag(self):
        return mark_safe(u'<img src="%s" width=500>' % self.dso_finder_chart_wide.url)
    
    def dso_finder_chart_tag(self):
        return mark_safe(u'<img src="%s" width=500>' % self.dso_finder_chart.url)

    def alt_az(self, location, utdt):
        """
        Get my Alt/Az at a given UTDT.
        """
        return get_alt_az(utdt, location.latitude, location.longitude, self.ra, self.dec)
    
    def shift_observing_dates(self, delta=0.):
        """
        Used?
        """
        # delta is in hours:  -2 = 10PM
        start_date, end_date, alt = self.observing_date_range
        if start_date is None:
            return None, None
        day_shift = round(-1 * 365. * delta / 24.) # earlier times are later in the calendar!
        new_start_date = start_date + dt.timedelta(days=day_shift)
        new_end_date = end_date + dt.timedelta(days=day_shift)
        return new_start_date, new_end_date, alt
    
    def shift_opposition_date(self, delta=0.):
        """
        Used?
        """
        day_shift = round(-1 * 365 * delta / 24.)
        new_opp_date = self.opposition_date + dt.timedelta(days=day_shift)
        return new_opp_date

    def object_is_up(self, location, utdt, min_alt=0.):
        """
        This is still used when creating an observing plan.
        Tests if a DSO is observable within a UTDT window.
        TODO V2: DEPRECATE!
        """
        az, alt, airmass = self.alt_az(location, utdt)
        if alt > min_alt:
            return True
        return False

    def get_absolute_url(self):
        """
        Django
        """
        return '/dso/{}'.format(self.pk)

    def save(self, *args, **kwargs):
        self.ra = self.ra_float # get from property
        self.dec = self.dec_float # get from property
        self.ra_text = self.format_ra # get from property
        self.dec_text = self.format_dec # get from property
        self.shown_name = create_shown_name(self)
        # Generate a DSO finder chart if one doesn't exist
        # Except you can't - it crashes everything, UNLESS
        # you run the code in it's own thread.  Why?  Who knows?
        # UPDATE: 2 Jan 2022 --- this might actually work now.
        # UPDATE: 1 Sep 2023 --- ARGH circular import hell.
        #try:
        #    fn = create_pdf_page(self)
        #    self.pdf_page.name = fn
        #except:
        #    pass

        super(DSO, self).save(*args, **kwargs)
        
    class Meta:
        verbose_name = 'Deep Sky Object'
        verbose_name_plural = 'DSOs'
        ordering = ['ra', 'dec']

    def __str__(self):
        if self.shown_name is None:
            return 'FOO'
        return self.shown_name
    
class DSOInField(DSOAbstract, models.Model):
    """
    This model exists because there are too many cases where DSOs are near other DSOs,
    OR that adjacent DSOs have some relationship to each other.  To avoid crowding,
    we define a DSO object to be a field of 1+ DSOs; with a primary and additional
    "DSOs in Field".
    """
    parent_dso = models.ForeignKey(DSO, on_delete=models.CASCADE)

    @property
    def label_on_chart(self):
        """
        These show up in the generated narrow-field view.
        """
        return self.shown_name
    
    @property
    def name_plus_alias(self):
        """
        Return the shown_name plus all aliases
        """
        main = self.shown_name
        full = []
        if self.aliases.count() > 0:
            for a in self.aliases.all():
                full.append(f"{a.catalog.abbreviation} {a.id_in_catalog}")
        if len(full) > 0:
            alist = ', '.join(full)
            main += f" ({alist})"
        return main
    
    @property
    def primary_distance(self):
        """
        Return the angular distance to the primary DSO
        """
        # angular separation in arcseconds
        sep = alt_get_small_sep(self.ra, self.dec, 
                self.parent_dso.ra, self.parent_dso.dec,
                unit='arcmin'
            )
        return sep
    
    @property
    def primary_angle(self):
        """
        Return the position angle from the primary DSO to the DSOInField
        """
        pa = get_simple_position_angle(self.parent_dso.ra, self.parent_dso.dec, self.ra, self.dec)
        return pa
    
    @property
    def alias_list(self):
        """
        Return a comma-separated alias list.
        TODO: Integrate aliases from SIMBAD/HyperLeda?
        """
        aliases = []
        if self.aliases.count() > 0:
            for alias in self.aliases.all():
                if alias.shown_name is None:
                    name = f"{alias.catalog.abbreviation} {alias.id_in_catalog}"
                else:
                    name = alias.shown_name
                aliases.append(name)
            return ', '.join(aliases)
        return ''

    def save(self, *args, **kwargs):
        self.ra = self.ra_float # get from property
        self.dec = self.dec_float # get from property
        self.ra_text = self.format_ra # get from property
        self.dec_text = self.format_dec # get from property
        self.shown_name = create_shown_name(self)
        super(DSOInField, self).save(*args, **kwargs)

    class Meta:
        verbose_name = 'Deep Sky Object in Field'
        verbose_name_plural = 'Deep Sky Objects in Field'
        ordering = ['-pk'] # ['ra', 'dec']  # TODO: What's the best ordering?

    def __str__(self):
        return f"{self.shown_name} in the field of {self.parent_dso.shown_name}"

class DSOAbstractAlias(models.Model):
    """
    This has all of the aliases for a DSO or a DSOInField
    There's a slight precedence in catalogs:
        - Messier
        - Caldwell
        - NGC
        - IC
        - Herschel 400
    so that M 52 = NGC 7654 = Cr 455 = Mel 243.
    Several search functions check aliases, so you SHOULD always reach the
    desired object.

    TODO V2: Use the precedence field for Catalog for ordering!
        This logic might be elsewhere...
    """

    catalog = models.ForeignKey('utils.Catalog', on_delete = models.CASCADE)
    id_in_catalog = models.CharField (
        _('ID'),
        max_length = 24
    )
    alias_in_field = models.PositiveIntegerField (
        _('Alias in Field'),
        default = NO,
        choices = INT_YES_NO,
        help_text = "Alias is for a field object."
    )
    in_field_dso = models.CharField (
        _('In Field DSO Name'),
        max_length = 20,
        null=True, blank=True
    )
    shown_name = models.CharField (
        _('Shown Name'),
        max_length = 100,
        null = True, blank = True
    )
    class Meta:
        abstract = True
        verbose_name = 'Alias'
        verbose_name_plural = 'Aliases'

    def __str__(self):
        return self.shown_name
    
class DSOAlias(DSOAbstractAlias):
    object = models.ForeignKey(DSO, 
        on_delete=models.CASCADE,
        related_name='aliases'
    )

    def save(self, *args, **kwargs):
        self.shown_name = create_shown_name(self, use_con=False)
        super(DSOAlias, self).save(*args, **kwargs)

class DSOInFieldAlias(DSOAbstractAlias):
    object = models.ForeignKey(DSOInField,
        on_delete=models.CASCADE,
        related_name='aliases'
    )

    def save(self, *args, **kwargs):
        self.shown_name = create_shown_name(self, use_con=False)
        super(DSOInFieldAlias, self).save(*args, **kwargs)

    def __str__(self):
        return f"{self.catalog.abbreviation} {self.id_in_catalog}"

class DSOImage(LibraryAbstractImage):
    """
    M:1 between uploaded images and a DSO.
    THESE ARE NOT GENERATED - they're uploaded from anywhere (e.g., an HST image of M 1).

    NOTE: The purpose of this table is to provide "cool" images of things to give the user
    an idea of what they really look like.

    HOWEVER, it's really not practical to seed them from anywhere.

    TODO V2: TRY to sort this out using the DSS/DSS2 or some series of image archives
        (PanSTARRS?)

    There are fields in LibraryAbstractImage that are unused in this model (exposure, processing_status)
    """
    object = models.ForeignKey(DSO,
        on_delete = models.CASCADE,
        related_name = 'images'
    )
    def __str__(self):
        out = self.object.shown_name
        return out
    
    class Meta:
        verbose_name = 'Image'
        verbose_name_plural = 'Images'

class DSOLibraryImage(LibraryAbstractImage):
    """
    These are USER-CREATED images of objects, i.e., from a Seestar/eQuinox or
    any camera system.
    """
    object = models.ForeignKey(
        DSO,
        on_delete = models.CASCADE,
        related_name = 'image_library'
    )
    ut_datetime = models.DateTimeField()

    @property
    def caption(self):
        x = ''
        if self.imaging_telescope is not None:
            x += f"{self.imaging_telescope}: "
        x += self.ut_datetime.strftime('%Y-%m-%d %H:%M UT')
        if self.exposure is not None:
            x += f', {self.exposure}min'
        if self.processing_status not in [None, 'None']:
            x += f', {self.get_processing_status_display()}'
        return x
    
    def __str__(self):
        return self.object.shown_name
    
    class Meta:
        verbose_name = 'DSO Library Image'
        verbose_name = 'DSO Library Images'

class DSOObservation(ObservingLog):
    """
    M:1 between observation records and DSOs.
    """
    object = models.ForeignKey(DSO,
        on_delete = models.CASCADE,
        related_name = 'observations'
    )

    # these probably should be class parameters.
    object_type = 'DSO'
    url_path = 'dso-detail'

    @property
    def observation_metadata(self):
        return get_metadata(self)

    @property
    def target_name(self):
        return self.object.shown_name

    @property
    def ra(self):
        return self.object.ra

    @property
    def dec(self):
        return self.object.dec

    @property
    def distance(self):
        return f"{self.object.distance} {self.object.distance_units}"

    def __str__(self):
        return f"{self.ut_datetime}: {self.object_type}: {self.object.shown_name}"
        
    class Meta:
        verbose_name = 'Observation'
        verbose_name_plural = 'Observations'
        ordering = ['-ut_datetime']

class DSOList(models.Model):
    """
    A user-create list of DSOs sharing some theme for observing.

    Typically, this will be used for "what I want to observe next time out".

    DSOs on an "Active" list will show up with the telescope icon on lists of DSOs;
    the idea is that you might want to keep older lists around for a while but don't 
    want to get confused about which objects you really intend to observe "next".
    """
    name = models.CharField (
        _('Name'),
        max_length = 100
    )
    description = models.TextField (
        _('Description'),
        null = True, blank = True
    )
    dso = models.ManyToManyField (DSO)
    tags = TaggableManager(blank=True)  # Used  TODO V2: come up with some use for this...
    show_on_plan = models.PositiveIntegerField ( # TODO V2: DEPRECATE?
        _('On Plan PDF'),
        choices = INT_YES_NO,
        default = 1,
        help_text = 'Set to YES/1 to add this to a PDF plan'
    )
    pdf_page = models.FileField (
        _('PDF Page'),
        null = True, blank = True,
        upload_to = 'dso_pdf' # TODO: Change this or remove it...
    )
    map_scaling_factor = models.FloatField (
        _('Map Scaling Factor'),
        default = 2.4,
        help_text = 'Map scaling: you prob. do not need to change this.'
    )
    active_observing_list = models.PositiveIntegerField (
        _('Active List'),
        choices = INT_YES_NO,
        default = NO,
        help_text = 'This is used for a back-reference on lists of DSOs'
    )

    def get_absolute_url(self):
        return '/dso/list/{}'.format(self.pk)

    @property
    def mid_ra(self):
        """
        Ugh - this won't work for things straddling 0h RA.
        """
        avg = self.dso.aggregate(avg=Avg('ra'))['avg']
        min_ra, max_ra = self.ra_range
        if max_ra - min_ra > 12:
            avg = avg - 12.
        if avg < 0:
            avg += 24.
        return avg
    
    @property
    def mid_dec(self):
        avg = self.dso.aggregate(avg=Avg('dec'))['avg']
        return avg

    @property
    def ra_range(self):
        ra_min = None
        ra_max = None
        for dso in self.dso.all():
            if ra_min is None or dso.ra < ra_min:
                ra_min = dso.ra
            if ra_max is None or dso.ra > ra_max:
                ra_max = dso.ra
        return (ra_min, ra_max)

    @property
    def dec_range(self):
        dec_min = None
        dec_max = None
        for dso in self.dso.all():
            if dec_min is None or dso.dec < dec_min:
                dec_min = dso.dec
            if dec_max is None or dso.dec > dec_max:
                dec_max = dso.dec
        return (dec_min, dec_max)

    @property
    def dso_count(self):
        return self.dso.count()
    
    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'DSO List'
        verbose_name_plural = 'DSO Lists'
        ordering = ['-pk']

class AtlasPlateAbstract(models.Model):
    """
    TODO: Bright Star Lists
    TODO: Double Stars?
    TODO: "Special" plates for things like the LMC/SMC/Virgo, etc. - These will need a different FOV, or 
        might be split up into sections...   Need to research.

    This is an abstract model so as to support "special" plates (e.g., close-ups of the
    Virgo cluster, or the LMC, etc.)
    """
    plate_id = models.PositiveIntegerField(_('Plate ID'), unique=True)
    slug = models.SlugField(unique=True)
    center_ra = models.FloatField(_('Center RA'))
    center_dec = models.FloatField(_('Center Dec'))
    radius = models.FloatField(_('Radius'), default=20.0)
    tags = TaggableManager(blank=True)
    dso = models.ManyToManyField(DSO, blank=True)
    constellation = models.ManyToManyField(Constellation, blank=True)

    @property
    def center_constellation(self):
        lookup = get_constellation(self.center_ra, self.center_dec)
        constellation = Constellation.objects.filter(abbreviation__iexact=lookup['abbr']).first()
        return constellation
    center_constellation.fget.short_description = 'Con.'

    @property
    def constellation_list(self):
        cc = []
        for c in self.constellation.all():
            cc.append(c.abbreviation)
        return ', '.join(cc)

    @property
    def dso_count(self):
        return self.dso.count()
    
    class Meta:
        abstract = True

class AtlasPlate(AtlasPlateAbstract):
    """
    Divide the sky into 258 plates, roughly 30° in diameter with overlap.
    Declinations: ±90°, 75°, 60°, 45°, 30°, 15°, 0°
    Right Ascensions: vary depending on the declination
        ±90°: n/a          ( 1 N/S each) =   2 total
        ±75°: every 2h     (12 N/S each) =  26 total
        ±60°: every 1h30m  (16 N/S each) =  58 total
        ±45°: every 1h12m  (20 N/S each) =  98 total
        ±30°: every 1h     (24 N/S each) = 146 total
        ±15°: every 0h45m  (32 N/S each) = 210 total
          0°: every 0h30m  (48 N/S each) = 258 total
    """
    @property
    def plate_title(self):
        return f"Plate {self.plate_id}: ({self.center_ra:.2f}h {self.center_dec}°) in {self.center_constellation}"

    @property
    def plate_images(self):
        """
        Create a dict of all available atlas plate image renditions.
        There should be 4:
            default        = black-on-white, symbols
            shapes         = black-on-white, shapes
            reversed       = white-on-black, symbols
            shapesreversed = white-on-black, shapes
        """
        vv = self.atlasplateversion_set.all()
        d = {}
        for v in vv:
            if v.shapes:
                k = 'shapesreversed' if v.reversed else 'shapes'
            else:
                k = 'reversed' if v.reversed else 'default'
            d[k] = v
        return d

    def save(self, *args, **kwargs):
        self.slug = self.plate_id
        super(AtlasPlate, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return '/atlas/{}'.format(self.plate_id)

    def __str__(self):
        return f"Plate {self.plate_id}"

    class Meta:
        verbose_name = 'Atlas Plate'
        verbose_name_plural = 'Atlas Plates'
        ordering = ['plate_id']

class AtlasPlateSpecial(AtlasPlateAbstract):
    """
    Still in development: create custom plates centering on some large-scale set of DSOs
        * LMC and SMC
        * Virgo Cluster (or portions thereof)
        * Sagittarius/Milky Way Center
    """
    title = models.CharField(
        _('Title'),
        max_length = 100
    )

    @property
    def plate_title(self):
        return f"Plate {self.plate_id}: {self.title} ({self.center_ra:.2f}h {self.center_dec}°) in {self.center_constellation}"

    def save(self, *args, **kwargs):
        self.slug = f'special-{self.plate_id}'
        super(AtlasPlateSpecial, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return '/atlas/special/{}'.format(self.plate_id)

    def __str__(self):
        return f"Special Plate {self.plate_id}: {self.title}"

class AtlasPlateVersionAbstract(models.Model):
    """
    Rendition of an Atlas Plate - Abstract
    """
    shapes = models.BooleanField(_('Shapes'), default=False)
    reversed = models.BooleanField('Reversed', default=False)

    def plate_tag(self):
        return mark_safe(u'<img src="%s" width=500>' % self.image.url)

    def __str__(self):
        return f"{self.plate.plate_id}: shapes={self.shapes} reversed={self.reversed}"

    class Meta:
        abstract = True

class AtlasPlateVersion(AtlasPlateVersionAbstract):
    """
    Rendition of an Atlas Plate
    """
    plate = models.ForeignKey(AtlasPlate, on_delete=models.CASCADE)
    image = models.ImageField(
        _('Plate'),
        upload_to = 'atlas_images',
        null = True, blank = True
    )

class AtlasPlateSpecialVersion(AtlasPlateVersionAbstract):
    plate = models.ForeignKey(AtlasPlateSpecial, on_delete=models.CASCADE)
    image = models.ImageField(
        _('Plate'),
        upload_to = 'atlas_images_special',
        null = True, blank = True
    )

class MilkyWay(models.Model):
    """
    Each row is a data point along a segment/contour of a particular level.
    There are >1 segments of each.
    """
    contour = models.PositiveIntegerField (_('Level'),help_text = '1 to 5, 5 being the most intense')
    segment = models.PositiveIntegerField (_('Segment #'),)
    longitude = models.FloatField (_('Longitude'),)
    ra = models.FloatField(_('R.A. 2000'))
    dec = models.FloatField(_('Dec. 2000'))

class AtlasPlateConstellationAnnotation(models.Model):
    """
    Each row is a position for a label on an Atlas Plate for a Constellation
    """
    plate = models.ForeignKey(AtlasPlate, on_delete=models.CASCADE)
    constellation = models.ForeignKey(Constellation, on_delete=models.CASCADE)
    ra = models.FloatField(_('R.A.'))
    dec = models.FloatField(_('Dec.'))

IMAGING_PRIORITY_OPTIONS = (
    (-1, 'None'),
    (0, 'Lowest'),
    (1, 'Low'),
    (2, 'Medium'),
    (3, 'High'),
    (4, 'Highest')
)
IMAGING_ISSUES_CHOICES = (
    ('lowdec', 'Low Declination'),
    ('angsize', 'Small Ang. Size'),
    ('dim', 'Low Surf. Brightness'),
    ('faint', 'Low V Magnitude'),
    ('questionable', 'Might not be possible')
)
class DSOImagingChecklist(models.Model):
    """
    Separate table for Imaging Priorities.
    TODO V2: DEPRECATE and rectify differences between TargetDSO* and these values.
    """
    priority = models.IntegerField(
        choices = IMAGING_PRIORITY_OPTIONS,
        null = True, blank = True
    )
    issues = models.CharField(
        _('Potential Issues'),
        choices = IMAGING_ISSUES_CHOICES,
        max_length = 20,
        null = True, blank = True
    )
    dso = models.ForeignKey(DSO, on_delete=models.CASCADE)
    # TODO: Add Telescope so we can have different imaging priorities for different scopes

    def get_absolute_url(self):
        return '/dso/{}'.format(self.dso.pk)
    
    def __str__(self):
        return self.dso.__str__()
    
    class Meta:
        verbose_name = 'Imaging Checklist DSO'
        verbose_name_plural = 'Imaging Checklist DSOs'
        ordering = ['-dso__dec']

class DSOObservingMode(models.Model):
    dso = models.ForeignKey('dso', on_delete=models.CASCADE)
    # The mode for this DSO?
    mode = models.CharField(
        _('Observing Mode'),
        max_length = 10,
        choices = OBSERVING_MODE_TYPES
    )
    # For this mode, how difficult will this DSO be?
    viable = models.PositiveSmallIntegerField(
        _('Viability'),
        choices = MODE_VIABILITY_CHOICES
    )
    # Priority: 0 = none to 4 highest
    priority = models.PositiveSmallIntegerField(
        choices=MODE_PRIORITY_CHOICES,
        null = True, blank = True # For now - this should be required post-seeding
    )
    # Is this DSO visually interesting for this mode?
    interesting = models.BooleanField(default=False)
    # Is this DSO a 'challenge' for this mode?
    challenging = models.BooleanField(default=False)
    # Notes on observing this DSO with this mode
    notes = models.TextField(null=True, blank=True)

    def notes_flag(self):
        if self.notes is None or len(self.notes.strip()) == 0:
            return ''
        return '*'
    
    def __str__(self):
        x = f"{self.dso}: {self.mode} ({self.priority}, {self.viable})"
        return x