from re import L, X
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.utils.html import mark_safe
from django.utils.translation import gettext as _
from ..tech.models import Telescope, Eyepiece

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

    def object_image_tag(self):
        return mark_safe(u'<img src="%s" width=500>' % self.image.url)

    class Meta:
        abstract = True

SEEING_CHOICES = (
    (5, 'Excellent: stable diffraction rings'),
    (4, 'Good: light undulations across diffraction rings'),
    (3, 'Fair: broken diffraction rings; central disk deformations'),
    (2, 'Poor: (partly) missing diffraction rings; eddy streams in central disk'),
    (1, 'Fail: boiling image; no sign of diffraction pattern')
)
class ObservingLog(models.Model):
    ut_date = models.DateField (
        _('Date of Obs'),
        help_text = 'UT Date'
    )
    ut_time = models.TimeField (
        _('Time of Obs'),
        help_text = 'UT Time'
    )
    # Seeing / Transparency / etc?
    seeing = models.PositiveIntegerField (
        _('Seeing'),
        choices = SEEING_CHOICES,
        null = True, blank = True
    )
    sqm = models.FloatField (
        _('SQM'),
        null = True, blank = True
    )
    # telescope
    telescope = models.ForeignKey (
        _(Telescope),
        default = 1,
        on_delete = models.CASCADE
    )
    # Eyepiece(s)
    eyepieces = models.ManyToManyField (
        _(Eyepiece),
    )
    # Filter(s)
    notes = models.TextField (
        _('Notes'),
        null = True, blank = True
    )
    # sketch?
    # images? - either from the ZWO camera or say a phone?

    class Meta:
        abstract = True
