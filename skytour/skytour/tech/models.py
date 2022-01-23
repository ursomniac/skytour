from django.db import models
from django.utils.html import mark_safe
from django.utils.translation import gettext as _

class Telescope(models.Model):

    name = models.CharField (
        _('Name'),
        max_length = 100
    )
    aperture = models.PositiveIntegerField (
        _('Aperture'),
        help_text = 'mm'
    )
    focal_length = models.PositiveIntegerField (
        ('Focal Length'),
        help_text = 'mm'
    )

    def __str__(self):
        return self.name

