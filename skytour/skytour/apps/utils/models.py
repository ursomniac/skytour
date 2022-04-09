from django.db import models
from django.utils.translation import gettext as _
from ckeditor.fields import RichTextField
from colorfield.fields import ColorField
from ..plotting.vocabs import MAP_SYMBOL_TYPES

class Catalog(models.Model):
    """
    One Catalog is Proper Name - it has an empty abbreviation.
    """
    name = models.CharField (
        _('Catalog Name'),
        max_length = 100
    )
    slug = models.SlugField (
        _('Slug')
    )
    abbreviation = models.CharField (
        _('Abbreviation'),
        max_length = 10
    )
    use_abbr = models.BooleanField (
        _('Use Abbr in List'),
        default = True
    )
    description = models.TextField (
        _('Description'),
        null=True, blank=True
    )

    @property
    def dso_count(self):
        """
        You need this separately because membership can be through a primary id OR an alias.
        """
        return self.dso_set.count() + self.dsoalias_set.count()

    class Meta:
        ordering = ['abbreviation']

    def get_absolute_url(self):
        return '/catalog/{}'.format(self.pk)

    def __str__(self):
        return self.abbreviation

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
    short_name = models.CharField (
        _('Short Name'),
        max_length = 40,
        null = True, blank = True
    )
    bgcolor = ColorField (
        _('Background Color'),
        default = '#666666'
    )
    # need icon field
    marker_type = models.CharField(
        _('Plot Marker Type'),
        max_length = 10,
        default = 'x'
    )
    marker_color = models.CharField(
        _('Marker Type Color'),
        max_length = 7,
        default = '#999'
    )
    map_symbol_type = models.CharField(
        _('Map Symbol Type'),
        choices = MAP_SYMBOL_TYPES,
        max_length = 30,
        default = 'marker'
    )
    code = models.CharField(
        _('Abbr. Code'),
        max_length = 4,
        null = True, blank = True
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
    map = models.ImageField (
        _('Map'),
        upload_to = 'constellation_maps',
        null=True, blank=True
    ) 
    other_map = models.ImageField ( # This ONLY exists because of Serpens
        _('Other Map'),
        upload_to = 'constellation_maps',
        null=True, blank=True
    )
    background = RichTextField (
        _('Background'),
        null = True, blank = True
    )
    historical_image = models.ImageField (
        _('Historical Map'),
        upload_to = 'historical_constellation_maps',
        null = True, blank = True
    )
    neighbors = models.ManyToManyField (
        'self',
        blank = True
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

