import math
from django.db import models
from django.utils.translation import gettext as _
from ..abstract.vocabs import YES_NO, YES
from .utils import *

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
        _('Focal Length'),
        help_text = 'mm'
    )
    order_in_list = models.PositiveIntegerField (
        _('Order in List'),
        default = 0
    )
    active = models.PositiveIntegerField (
        _('Active'),
        choices = YES_NO,
        default = YES,
        help_text='If active will show up on drop-downs for telescopes'
    )
    is_default = models.BooleanField (
        _('Is Default'),
        default = False
    )
    uses_eyepiece = models.BooleanField (
        _('Uses Eyepieces'),
        default = False,
        help_text = 'False for Imaging/Smart Telescopes'
    )
    include_on_finder = models.BooleanField (
        _('Include on Finder Charts'),
        default = True,
        help_text='Add FOV when creating finder charts'
    )
    stellarium_telescope = models.PositiveIntegerField (
        _('Stellarium Telescope #'),
        null = True, blank = True,
        help_text = 'in Stellarium, the Telescope #'
    )
    stellarium_sensor = models.PositiveIntegerField (
        _('Stellarium Sensor #'),
        null = True, blank = True,
        help_text = 'in Stellarium, the Sensor #'
    )
 
    @classmethod
    def get_default_telescope(self):
        tel = Telescope.objects.filter(is_default=True).first()
        if tel is not None:
            return tel
        return Telescope.objects.first()

    @property
    def f_ratio(self):
        return get_telescope_f_ratio(self.focal_length, self.aperture)

    @property
    def limiting_magnitude(self):
        return get_telescope_limiting_magnitude(self.aperture)

    @property
    def raleigh_limit(self):
        return get_telescope_raleigh_limit(self.aperture)

    @property
    def dawes_limit(self):
        return get_telescope_dawes_limit(self.aperature)
    
    @property
    def in_stellarium(self):
        return None not in (self.stellarium_telescope, self.stellarium_sensor)
    
    class Meta:
        ordering = ['order_in_list']

    def save(self, *args, **kwargs):
        # Handle default
        if self.is_default:
            Telescope.objects.filter(is_default=True).update(is_default=False)
        super(Telescope, self).save(*args, **kwargs)
        return
        
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
        return get_eyepiece_magnification(self.telescope.focal_length, self.focal_length)

    @property
    def field_of_view(self):
        return get_eyepiece_field_of_view(self.apparent_fov, self.magnification)

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

# TODO V2: Need to make this standalone but ALSO accessible to a Telescope for options
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


class Sensor(models.Model):
    """
    This is for camera, etc. that go with a telescope.
    """
    telescope = models.ForeignKey(
        Telescope,
        on_delete = models.SET_NULL,
        null = True, blank = True
    )
    name = models.CharField (
        _('Sensor Name'),
        max_length = 30,
        default = 'Onboard camera'
    )
    pixels_x = models.PositiveIntegerField (
        _('Pixels X')
    )
    pixels_y = models.PositiveIntegerField (
        _('Pixels Y')
    )
    pixel_size = models.FloatField (
        _('Pixel Size'),
        help_text = 'in microns: µm'
    )
    camera_name = models.CharField (
        _('Camera Name'),
        max_length = 30,
        null = True, blank = True
    )
    order_in_list = models.PositiveIntegerField (
        _('Order in List'),
        default = 1
    )

    @property
    def field_of_view(self):
        return get_sensor_field_of_view(self.telescope.focal_length, self.pixels_x, self.pixels_y, self.pixel_size)
    
    @property
    def pixel_resolution(self):
        return get_sensor_pixel_resolution(self.telescope.focal_length, self.pixel_size)
    
    @property
    def megapixels(self):
        return get_sensor_megapixels(self.pixels_x, self.pixels_y)
    
    def __str__(self):
        c = self.camera_name if self.camera_name is not None else 'FIX'
        try:
            back = f"{self.telescope.name}: {self.name} ({c}) = {self.megapixels:.1f}MP ({self.pixels_x}x{self.pixels_y})"
            return back
        except:
            return "Something stupid happened"
        
    class Meta:
        ordering = ['order_in_list']