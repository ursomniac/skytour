import pytz
from django.db import models
from django.urls import reverse
from django.utils.html import mark_safe
from django.utils.translation import gettext as _
from ..misc.models import TimeZone, StateRegion, Country
from ..astro.utils import get_limiting_magnitude, get_declination_range
from .pdf import create_pdf_form
from .utils import get_mean_obs_sqm, get_effective_bortle
from .vocabs import CARDINAL_DIRECTIONS, STATUS_CHOICES

class ObservingLocation(models.Model):
    #
    ### LOCATION FIELDS
    name = models.CharField (
        _('Name'),
        max_length = 100,
        null = True,
        blank = True
    )
    street_address = models.CharField (
        _('Street Address'),
        max_length = 200,
        null = True, blank = True
    )
    city = models.CharField (
        _('City'),
        max_length = 50
    )
    state = models.ForeignKey (
        StateRegion,
        null = True, blank = True,
        on_delete = models.SET_NULL
    )
    region = models.CharField (
        _('Region/Country'),
        max_length = 100,
        blank=True, null=True,
        help_text = 'For outside US/Canada'
    )
    country = models.ForeignKey (
        Country, 
        null = True, blank = True,
        on_delete = models.CASCADE
    )
    status = models.CharField (
        _('Status'),
        max_length = 50,
        choices = STATUS_CHOICES,
        default = 'TBD'
    )
    is_default = models.BooleanField (
        _('Default Location'),
        default = False
    )
    #
    ### GEOSPATIAL FIELDS
    latitude = models.FloatField (
        _('Latitude')
    )
    longitude = models.FloatField (
        _('Longitude')
    )
    elevation = models.FloatField (
        _('Elevation'),
        help_text = 'meters'
    )
    time_zone = models.ForeignKey (
        TimeZone,
        on_delete = models.CASCADE
    )
    travel_distance = models.FloatField (
        _('Dist.'),
        null = True, blank = True
    )
    travel_time = models.FloatField (
        _('Tr. Time'),
        null = True, blank = True,
        help_text = 'minutes'
    )
    #
    ### SKY BRIGHTNESS FIELDS
    sqm = models.FloatField (
        _('SQM'),
        null = True, blank = True,
        help_text = 'mag/arcsec^2'
    )
    brightness = models.FloatField (
        _('Brightness'),
        null = True, blank = True,
        help_text = 'mcd/m^2'
    )
    artificial_brightness = models.FloatField (
        _('Artif. Brightness'),
        null = True, blank = True,
        help_text = 'µcd/m^2'
    )
    ratio = models.FloatField (
        _('Ratio'),
        null = True, blank = True,
        help_text = 'artificial to natural brightness'
    )
    bortle = models.PositiveIntegerField (
        _('Bortle')
    )

    # 
    ### SITE FIELDS
    parking = models.CharField (
        _('Parking Available'),
        max_length = 200,
        null = True, blank = True
    )
    is_flat = models.BooleanField (
        _('Is Flat'),
        null = True
    )
    description = models.TextField (
        _('Description'),
        null = True, blank = True
    )
    light_sources = models.TextField (
        _('Light Sources'),
        null = True, blank = True
    )
    horizon_blockage = models.TextField (
        _('Horizon Blockage'),
        null = True, blank = True,
        help_text = 'describe cardinal directions with approximate altitude blocked, and/or other issues (buildings, etc.)'
    )
    #
    ### MAPS
    map_image = models.ImageField (
        _('Google Map Image'),
        null = True, blank = True,
        upload_to = 'street_maps/'
    )
    earth_image = models.ImageField (
        _('Google Earth Image'),
        null = True, blank = True,
        upload_to = 'earth_maps/'
    )
    bortle_image = models.ImageField (
        _('Bortle Map'),
        null = True, blank = True,
        upload_to = 'bortle_maps/'
    )
    #
    ### FORM
    pdf_form = models.FileField ( 
        _('PDF Form'),
        upload_to = 'media/location_pdf/',
        null = True, blank = True
    )
    def map_tag(self):
        return mark_safe(u'<img src="%s" width=500>' % self.map_image.url)
    def earth_tag(self):
        return mark_safe(u'<img src="%s" width=500>' % self.earth_image.url)
    def bortle_tag(self):
        return mark_safe(u'<img src="%s" width=500>' % self.bortle_image.url)

    @classmethod
    def get_default_location(cls):
        obj = cls.objects.filter(is_default=True).first()
        if obj is not None:
            return obj
        return cls.objects.first()
    
    @property
    def plotting_marker_type(self):
        if self.state:
            return self.state.marker
        return 'x'
    
    @property
    def region_name(self):
        if self.state:
            return self.state.name
        return self.region
    
    @property
    def short_region_name(self):
        if self.state:
            return self.state.abbreviation
        return self.region
    
    @property
    def elevation_feet(self):
        if self.elevation:
            return self.elevation * 39.37 / 12.
        return None
        
    @property
    def placename(self):
        x = "{}, {}: {}".format(self.city, self.region_name, self.street_address)
        if self.name:
            x += " ({})".format(self.name)
        return x

    @property
    def coords(self):
        return "{:.2f}, {:.2f}".format(self.latitude, self.longitude)

    @property
    def status_color(self):
        colors = {
            'TBD': '#666', 
            'Active': '#060', 
            'Provisional': '#006',
            'Issues': '#960',
            'Possible': '#066', 
            'Rejected': '#600'
        }
        if self.status in colors.keys():
            return colors[self.status]
        return '#C69'

    @property
    def name_for_header(self):
        x = "{}, {} {}".format(self.street_address, self.city, self.region_name)
        if self.name:
            x = "{}: ".format(self.name) + x
        return x

    @property
    def short_name(self):
        return f"{self.city}, {self.state.short_region_name}: {self.name}"

    @property
    def limiting_magnitude(self):
        return get_limiting_magnitude(self.bortle)

    @property
    def my_time_zone(self):
        pz = self.time_zone.pytz_name
        return pytz.timezone(pz)

    @property
    def number_of_sessions(self):
        x = self.observingsession_set.count()
        return x

    @property
    def last_session(self):
        x = self.observingsession_set.order_by('-ut_date').first()
        if x:
            return x.ut_date
        return None

    @property
    def mean_obs_sqm(self):
        mean, rms = get_mean_obs_sqm(self)
        return (mean, rms)
    
    @property
    def mean_obs_bortle(self):
        sqm, rms = self.mean_obs_sqm
        if sqm is None:
            return (None, None)
        b_avg = get_effective_bortle(sqm)
        if rms is not None:
            b_low = get_effective_bortle(sqm - rms)
            b_high = get_effective_bortle(sqm + rms)
            b_rms = abs(b_high - b_low) / 2. # crude, but it'll work
        else:
            b_rms = None
        return (b_avg, b_rms)

    @property
    def effective_bortle(self):
        return get_effective_bortle(self.sqm)
    
    @property
    def declination_range(self):
        return get_declination_range(self)
    
    @property
    def minimum_declination(self):
        return self.declination_range[0]
    
    @property
    def maximum_declination(self):
        return self.declination_range[1]

    def get_absolute_url(self):
        return reverse('observing-location-detail', kwargs={'pk': self.pk})
        #return '/observing_location/{}'.format(self.pk)

    def __str__(self):
        if self.name:
            tag = "{}: {}".format(self.name, self.street_address)
        else:
            tag = self.street_address

        return "{}: {} | {} {}, {}".format(
            self.pk, self.status, tag, self.city, self.region_name
        )

    def save(self, *args, **kwargs):
        try:
            filename = create_pdf_form(self)
            self.pdf_form.name = filename
        except:
            pass
        # Handle default
        if self.is_default:
            ObservingLocation.objects.filter(is_default=True).update(is_default=False)
        super(ObservingLocation, self).save(*args, **kwargs)
        return

    class Meta:
        ordering = ['travel_distance']
 

class LocationImage(models.Model):
    location = models.ForeignKey('ObservingLocation', on_delete = models.CASCADE)
    image = models.ImageField (
        _('Image'),
        upload_to = 'location_images/'
    )
    description = models.TextField (
        _('Description'),
        null = True, blank = True
    )
    direction = models.CharField (
        _('Direction'),
        max_length = 2,
        choices = CARDINAL_DIRECTIONS,
        null = True, blank = True
    )

    def image_tag(self):
        return mark_safe(u'<img src="%s" width=500>' % self.image.url)


class ObservingLocationMask(models.Model):
    """
    Example:
     (a1, h1)
     (a2, h1) -> this creates a straight altitude line from a1->a2
     (a3, h3) -> this creates an interpolated altitude line from a2->a3
     (a4, h3) -> this creates another straight altitude line from a3->a4
     (a4, h1) -> this starts a straight line at a4
     (a5, h1) -> this creates a straight altitude line from a4->a5

     When making lines, starting azimuth is considered inclusive; ending azimuth is exclusive;
     i.e., 50° to 65° at 15° then 65° to 90° at 20°  it's 15° for az >= 50 and < 65;
     but 20° for az >= 65 and < 90, and so on.

     When defining - start at 0° and end at 360°.
    """
    location = models.ForeignKey(ObservingLocation, on_delete=models.CASCADE)
    azimuth_start = models.FloatField(
        _('Azimuth Start'),
        help_text='Inclusive - start at 0°'
    )
    azimuth_end = models.FloatField (
        _('Azimuth End'),
        help_text = 'Exclusive'
    )
    altitude_start = models.FloatField(_('Altitude Start'))
    altitude_end = models.FloatField(_('Altitude End'))

    class Meta:
        ordering = ['azimuth_start']

    def __str__(self):
        x = self.location.name
        start = f"({self.azimuth_start:5.1f}, {self.altitude_start:4.1f})"
        end = f"({self.azimuth_end:5.1f}, {self.altitude_end:4.1f})"
        return f"{x}: {start} - {end}"