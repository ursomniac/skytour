from re import L, X
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.utils.html import mark_safe
from django.utils.translation import gettext as _
from colorfield.fields import ColorField

class Catalog(models.Model):
    """
    One Catalog is Proper Name - it has an empty abbreviation.
    """
    name = models.CharField (
        _('Catalog Name'),
        max_length = 100
    )
    abbreviation = models.CharField (
        _('Abbreviation'),
        max_length = 10
    )
    use_abbr = models.BooleanField (
        _('Use Abbr in List'),
        default = True
    )

    class Meta:
        ordering = ['abbreviation']

    def get_absolute_url(self):
        return '/catalog/{}'.format(self.pk)

    def __str__(self):
        return self.abbreviation

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

class ObjectType(models.Model):
    """
    DSO Object Types
    """
    name = models.CharField(
        _('Name'),
        max_length = 200
    )
    slug = models.SlugField(
        _('Slug'),
        unique = True
    )
    bgcolor = ColorField (
        _('Background Color'),
        default = '#666666'
    )
    # need icon field
    marker_type = models.CharField(
        _('Plot Marker Type'),
        max_length = 1,
        default = 'x'
    )

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']

class Constellation(models.Model):
    """
    CV of the constellations.
    """
    name = models.CharField(
        _('Name'),
        max_length = 80
    )
    abbreviation = models.CharField (
        _('Abbreviation'),
        max_length = 3
    )
    slug = models.SlugField (
        _('Slug'),
        #unique = True
        default = 'xxx'
    )
    genitive = models.CharField (
        _('Genitive'),
        max_length = 80
    )

    def get_absolute_url(self):
        return '/constellation/{}'.format(self.slug)

    class Meta:
        ordering = ['abbreviation']

    def __str__(self):
        return self.abbreviation

    def save(self, *args, **kwargs):
        self.slug = self.abbreviation
        super(Constellation, self).save(*args, **kwargs)

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

class ObservingLog(models.Model):
    ut_date = models.DateField (
        _('Date of Obs'),
        help_text = 'UT Date'
    )
    ut_time = models.TimeField (
        _('Time of Obs'),
        help_text = 'UT Time'
    )
    # telescope
    # Eyepiece
    # Filters
    notes = models.TextField (
        _('Notes'),
        null = True, blank = True
    )

    class Meta:
        abstract = True
