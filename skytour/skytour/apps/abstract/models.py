import datetime
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.utils.html import mark_safe
from django.utils.translation import gettext as _
from ..observe.models import ObservingLocation
from ..session.models import ObservingSession
from ..site_parameter.helpers import find_site_parameter
from ..tech.models import Telescope, Eyepiece, Filter
from ..astro.transform import get_cartesian
from .vocabs import IMAGING_STATUS_CHOICES, IMAGING_PROCESSING_CHOICES, YES_NO

class FieldView(models.Model):
    """
    This is a model for the FOV map.
    """
    field_view = models.ImageField (
        _('Field View'),
        upload_to = 'field_view/',
        null = True, blank = True
    )

    def field_view_tag(self):
        return mark_safe(u'<img src="%s" width=500>' % self.field_view.url)

    class Meta:
        abstract = True

##### Abstract Models
class Coordinates(models.Model):
    """
    For now I'm storing them as separate fields.
    I had thought maybe as a string that I could parse.
    Might still try that.
    """
    ra_h = models.PositiveIntegerField ( 
        _('RA: hr'),
        validators=[MaxValueValidator(23)]
    )
    ra_m = models.PositiveIntegerField (
        _('min'),
        validators=[MaxValueValidator(59)]
    )
    ra_s = models.FloatField (
        _('sec'),
        validators=[
            MinValueValidator(0.000),
            MaxValueValidator(59.9999999)
        ],
        null = True, blank = True
    )
    # These are both set in the save()
    ra = models.FloatField (
        _('R.A.'),
        null = True, blank = True
    )
    ra_text = models.CharField (
        _('R.A. Text'),
        max_length = 16,
        null = True, blank = True
    )
    ### Dec.
    dec_sign = models.CharField (
        _('Dec: Sign'),
        max_length = 1,
        choices = ( ('+', '+'), ('-', '-') )
    )
    dec_d = models.IntegerField (
        _('deg'),
        validators=[
            MinValueValidator(0),
            MaxValueValidator(89)
        ]
    )
    dec_m = models.PositiveIntegerField (
        _('min'),
        validators = [MaxValueValidator(59)]
    )
    dec_s = models.FloatField (
        _('sec'),
        validators = [
            MinValueValidator(0.000),
            MaxValueValidator(59.9999999)
        ],
        null = True, blank = True
    )
    # These are both set in the save()
    dec = models.FloatField (
        _('Dec.'),
        null = True, blank = True
    )
    dec_text = models.CharField (
        _('Dec. Text'),
        max_length = 16,
        null = True, blank = True
    )

    @property
    def ra_float(self):
        x = self.ra_h + self.ra_m/60. 
        if self.ra_s:
            x += self.ra_s/3600. 
        return x
    @property
    def dec_float(self):
        x = self.dec_d + self.dec_m/60. 
        if self.dec_s: 
            x += self.dec_s/3600. 
        if self.dec_sign == '-':
            x *= -1.0
        return x

    @property
    def format_ra(self):
        return "{:02d}h {:02d}m {:05.2f}s".format(
            self.ra_h, self.ra_m, self.ra_s
        )

    @property
    def format_dec(self):
        return u"{}{:02d}° {:02d}\' {:05.2f}\"".format(
            self.dec_sign, self.dec_d, self.dec_m, self.dec_s
        )

    @property
    def short_ra_dec(self):
        rah = int(self.ra)
        ram = (self.ra - rah) * 60.
        des = '-' if self.dec < 0 else '+'
        dex = abs(self.dec) + 0.00015 # rounding
        ded = int(dex)
        dem = (dex - ded) * 60.
        return f"{rah:02d}h{ram:04.1f}m {des}{ded:02d}°{dem:04.1f}\'"
    
    @property
    def get_xyz(self):
        return get_cartesian(self.ra_float, self.dec_float, ra_dec = True)

    class Meta:
        abstract = True


class ObjectImage(models.Model):
    image = models.ImageField (
        _('Image'),
        upload_to = 'object_image/'
    )
    notes = models.TextField (
        _('Notes'),
        blank = True, null = True
    )
    order_in_list = models.PositiveIntegerField (
        _('Order'),
        default = 1
    )
    amateur_image = models.BooleanField (
        _('Amateur Image'),
        default = None,
        null = True
    )
    own_image = models.PositiveIntegerField (
        _('My Own Image'),
        default = 0,
        choices = YES_NO
    )
    exposure = models.FloatField (
        _('Image Exposure'),
        null = True, blank = True
    )
    processing_status = models.CharField (
        _('Image Processing Status'),
        max_length = 30,
        null = True, blank = True,
        choices = IMAGING_PROCESSING_CHOICES
    )

    def object_image_tag(self):
        return mark_safe(u'<img src="%s" width=500>' % self.image.url)

    class Meta:
        abstract = True


class ObservingLog(models.Model):
    session = models.ForeignKey(ObservingSession, null=True, on_delete=models.CASCADE)
    ut_datetime = models.DateTimeField (
        _('UTDT of Obs.'),
        default = datetime.datetime.utcnow,
        help_text = 'Date/Time (UT)'
    )
    # telescope
    telescope = models.ForeignKey (
        _(Telescope),
        default = 1,
        on_delete = models.CASCADE
    )
    # Eyepiece(s)
    eyepieces = models.ManyToManyField (Eyepiece, blank=True)
    # Filter(s)
    filters = models.ManyToManyField (Filter, blank=-True)
    # Ugh you need location!
    location = models.ForeignKey (
        ObservingLocation,
        default = find_site_parameter('default-location-id', default=48, param_type='positive'),
        on_delete = models.CASCADE,
        limit_choices_to = {'status__in': ['Active', 'Provisional']}
    )
    # Image metadata if imaged
    num_images = models.PositiveIntegerField(default=0, blank=True, null=True)
    imaging_status = models.IntegerField(
        choices = IMAGING_STATUS_CHOICES,
        default = 0,
        null=True, blank=True
    )

    # Filter(s)
    notes = models.TextField (
        _('Notes'),
        null = True, blank = True
    )

    @property
    def eyepiece_list(self):
        elist = [e.short_name for e in self.eyepieces.all()]
        return ', '.join(elist)

    @property
    def filter_list(self):
        flist = [f.short_name for f in self.filters.all()]
        return ', '.join(flist)

    class Meta:
        abstract = True

class ObservableObject(models.Model):
    
    @property
    def last_observed(self):
        obs = self.observations.order_by('-ut_datetime').first()
        if obs is None:
            return None
        return obs.ut_datetime

    @property
    def number_of_observations(self):
        x = self.observations.count()
        return x

    class Meta:
        abstract=True