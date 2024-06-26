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
    short_name = models.CharField (
        _('Short Name'),
        max_length = 10,
        null = True, blank = True
    )
    telescope = models.ForeignKey (Telescope, on_delete=models.SET_NULL, null=True, blank=True)

    @property
    def magnification(self):
        x = self.telescope.focal_length / self.focal_length
        m = int(10.*(x + 0.05))/10.
        return  m

    @property
    def field_of_view(self):
        return self.apparent_fov / self.magnification # degrees

    @property
    def fov_display(self):
        fov = self.field_of_view
        return f'{fov:6.3f}° = {fov*60.:7.2f}\''

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

FILTER_TYPE_CHOICES = (
    ('wide', 'Wide'),
    ('narrow', 'Narrow')
)

class Filter(models.Model):
    name = models.CharField (
        _('Name'),
        max_length = 40
    )
    short_name = models.CharField (
        _('Short Name'),
        max_length=10,
        null = True, blank = True
    )
    filter_type = models.CharField (
        _('Filter Type'),
        max_length = 40,
        choices = FILTER_TYPE_CHOICES
    )
    central_wavelength = models.FloatField (
        null = True, blank = True,
        help_text = 'in nm'
    )
    fwhm = models.FloatField (
        _('FWHM'),
        null = True, blank = True,
        help_text = 'in nm'
    )
    dominant_wavelength = models.FloatField (
        _('Dom. Wavelength'),
        null = True, blank = True,
        help_text = 'From Watten Specs, in nm'
    )
    transmission = models.FloatField (
        _('Transmission'),
        null = True, blank = True,
        help_text = 'in %'
    )
    transmission_curve = models.ImageField (
        _('Trans. Curve'),
        upload_to = 'filter_specs',
        null = True, blank = True
    )
    watten_curve = models.ImageField (
        _('Watten Curve'),
        upload_to = 'filter_specs',
        null = True, blank = True
    )
    notes = models.TextField (
        _('Notes'),
        null = True, blank = True
    )
    tech_notes = models.TextField (
        _('Tech Notes'),
        null = True, blank = True,
        help_text = 'From Watten specs'
    )

    def __str__(self):
        x = f'{self.name} ({self.filter_type})'
        if self.central_wavelength:
            x += f': {self.central_wavelength }'
            if self.fwhm:
                x += f'± {self.fwhm/2.}'
            x += ' nm'
        return x

    class Meta:
        ordering = ['central_wavelength']

