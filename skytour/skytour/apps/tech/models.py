import math
from django.db import models
from django.utils.html import mark_safe
from django.utils.translation import gettext as _

class Telescope(models.Model):

    name = models.CharField (
        _('Name'),
        max_length = 100
    )
    aperture = models.FloatField (
        _('Aperture'),
        help_text = 'mm'
    )
    focal_length = models.PositiveIntegerField (
        ('Focal Length'),
        help_text = 'mm'
    )

    @property
    def f_ratio(self):
        return self.focal_length / self.aperture

    @property
    def limiting_magnitude(self):
        #method_1 = 3.7 + 2.5 * math.log10(self.aperture**2)
        method_2 = 9.5 + 5.0 * math.log10(self.aperture/25.4)
        return method_2

    @property
    def raleigh_limit(self):
        """
        Basically, the limit at which two stars can be seed as two separate objects
        """
        theta = 138 / self.aperture # for 550 nm
        return theta

    @property
    def dawes_limit(self):
        theta = 116 / self.aperture
        return theta

    def __str__(self):
        return self.name

class Eyepiece(models.Model):
    type = models.CharField(
        _('Eyepiece Type'),
        default = 'Plossi',
        max_length = 50,
        null = True, blank = True
    )
    focal_length = models.FloatField (
        _('Focal Length'),
        help_text = 'mm'
    )
    apparent_fov = models.FloatField (
        _('App. FOV'),
        default = 52,
        help_text = 'degrees'
    )
    telescope = models.ForeignKey (Telescope, on_delete=models.SET_NULL, null=True, blank=True)

    @property
    def magnification(self):
        return self.telescope.focal_length / self.focal_length

    @property
    def mag_display(self):
        return f'{self.magnification:5.1f}'

    @property
    def field_of_view(self):
        return self.apparent_fov / self.magnification # degrees

    @property
    def fov_display(self):
        fov = self.field_of_view
        return f'{fov:6.3f}° = {fov*60.:7.3f}\''

    @property 
    def map_circle_radius(self, map_fov):
        """
        You'd use this e.g., to put an eyepiece onto the map.
        
        AFAICT:  
            1° = 0.004365  units
            1' = 7.2752e-5 units
        """
        return self.field_of_view * 0.004365

    def __str__(self):
        return f"{self.type} {self.focal_length} mm"

    class Meta:
        ordering = ['-focal_length']


    
