from django.db import models
from django.utils.translation import gettext as _

class AbstractSiteParameter(models.Model):
    date_created = models.DateTimeField(
        _('Date Created'),
        auto_now_add = True
    )
    date_modified = models.DateTimeField(
        _('Date Modified'),
        auto_now = True
    )
    title = models.CharField (
        _('Title'),
        max_length = 80
    )
    slug = models.SlugField (
        _('Slug')
    )
    description = models.TextField (
        _('Description'),
        null = True, blank = True
    )

    class Meta:
        abstract = True
        ordering = ['slug']

class SiteParameterPositiveInteger (AbstractSiteParameter):
    value = models.PositiveIntegerField (
        _('Value'),
        default = 0
    )

    def __str__(self):
        return "{} = {}".format(self.title, self.value)

class SiteParameterNumber (AbstractSiteParameter):
    value = models.IntegerField (
        _('Value'),
        default = 0
    )

    def __str__(self):
        return "{} = {}".format(self.title, self.value)

class SiteParameterFloat (AbstractSiteParameter):
    value = models.FloatField (
        _('Value'),
        default = 0.
    )

    def __str__(self):
        return "{} = {}".format(self.title, self.value)

class SiteParameterString (AbstractSiteParameter):
    value = models.CharField (
        _('Value'),
        default = '',
        max_length = 200
    )

    def __str__(self):\
        return "() = ()".format(self.title, self.value)

class SiteParameterLink (AbstractSiteParameter):
    value = models.URLField (
        _('URL'),
    )
    link_text = models.CharField (
        _('Link Text'),
        max_length = 200,
        null = True, blank = True
    )
    new_window = models.BooleanField (
        _('Opens New Window'),
        default = True,
        null = True, blank = True
    )
    
class SiteParameterImage (AbstractSiteParameter):
    value = models.ImageField (
        _('Image'),
    )
    upload_to = 'site_parameter_images'

class SiteParameterPDFFile(AbstractSiteParameter):
    value = models.FileField (
        _('PDF File'),
        upload_to = 'pdf_files'
    )