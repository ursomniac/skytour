from django.db import models
from django.utils.html import mark_safe
from django.utils.translation import gettext as _
from ..misc.models import TimeZone, StateRegion
from ..astro.utils import get_limiting_magnitude
from .pdf import create_pdf_form

CARDINAL_DIRECTIONS = [
    ('N', 'North'),
    ('NE', 'Northeast'),
    ('E', 'East'),
    ('SE', 'Southeast'),
    ('S', 'South'),
    ('SW', 'Southwest'),
    ('W', 'West'),
    ('NW', 'Northwest')
]
STATUS_CHOICES = [
    ('TBD', 'TBD'),
    ('Possible', 'Possible'),
    ('Issues', 'Issues'),
    ('Provisional', 'Provisional'),
    ('Active', 'Active'),
    ('Rejected', 'Rejected'),
]

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
        on_delete = models.CASCADE
    )
    status = models.CharField (
        _('Status'),
        max_length = 50,
        choices = STATUS_CHOICES,
        default = 'TBD'
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

    @property
    def elevation_feet(self):
        if self.elevation:
            return self.elevation * 39.37 / 12.
        return None
        
    @property
    def placename(self):
        x = "{}, {}: {}".format(self.city, self.state, self.street_address)
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
        x = "{}, {} {}".format(self.street_address, self.city, self.state.abbreviation)
        if self.name:
            x = "{}: ".format(self.name) + x
        return x

    @property
    def limiting_magnitude(self):
        return get_limiting_magnitude(self.bortle)


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

    def get_absolute_url(self):
        return '/observing_location/{}'.format(self.pk)

    def __str__(self):
        if self.name:
            tag = "{}: {}".format(self.name, self.street_address)
        else:
            tag = self.street_address

        return "{}: {} | {} {}, {}".format(
            self.pk, self.status, tag, self.city, self.state.abbreviation
        )

    def save(self, *args, **kwargs):
        filename = create_pdf_form(self)
        self.pdf_form.name = filename
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


        