import math
from django.db import models
from django.utils.translation import gettext as _
from djangoyearlessdate.models import YearlessDateField
from skyfield.api import Star
from .abstract import OrbitalElements

class Planet(models.Model):
    name = models.CharField (
        _('Name'),
        max_length = 20,
    )
    slug = models.SlugField (
        _('Slug'),
        null=True, blank=True
    )
    load = models.CharField (
        _('BSP File Name'),
        max_length = 20,
        null=True, blank=True
    )
    diameter = models.FloatField (
        _('Diameter'),
        help_text = 'Kilometers'
    )
    semi_major_axis = models.FloatField (
        _('Semi-Major Axis'),
        null = True, blank = True,
        help_text = 'au'
    )
    moon_names = models.CharField (
        _('Moon Names'),
        max_length = 100,
        null=True, blank=True,
        help_text = 'List of moons that might be observable; separate with commas'
    )

    planet_map = models.ImageField(
        _('Planet Map'),
        null=True, blank=True,
        upload_to='planet_maps'
    )
    @property
    def target(self):
        return "{} Barycenter".format(self.name)

    @property
    def moon_list(self):
        if not self.moon_names:
            return None
        mlist = []
        for m in self.moon_names.split(','):
            mlist.append(m.strip())
        return mlist

    def get_absolute_url(self):
        return '/planet/{}'.format(self.slug)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['semi_major_axis']

"""
SOMEHOW I want to add in moon metadata, like apparent magnitude which DOES
vary depending on Earth-planet distance, and also in the case of Iapetus.

Moons: 
    Ph  vga = 0.07, r = 13.0 x 11.4 x 9.1
    De  vga = 0.08, r = 7.8 x 6.0 x 5.1

    Io  vga = 0.62, r = 1821.5
    Eu  vga = 0.68, r = 1560.8
    Ga  vga = 0.44, r = 2631.2
    Ca  vga = 0.19, r = 2410.3

    Mi  vga = 0.6,  r = 208 x 197 x 191
    En  vga = 1.0,  r = 257 x 251 x 248
    Te  vga = 0.8,  r = 538 x 528 x 526
    Di  vga = 0.7,  r = 563 x 561 x 560
    Rh  vga = 0.7,  r = 765 x 763 x 762
    Ti  vga = 0.22, r = 2575.
    Ia  vga = 0.05 to 0.5, r = 746 x 746 x 712

    Ob  vga = 0.23, r = 761.4
    Ti  vga = 0.27, r = 788.9

    Tr  vga = 0.72, r = 1353.4
"""



class MeteorShower(models.Model):

    name = models.CharField(
        _('Name'),
        max_length = 50
    )
    slug = models.SlugField(
        _('Slug')
    )
    start_date = YearlessDateField (
        _('Start Date')
    )
    end_date = YearlessDateField (
        _('End Date')
    )
    peak_date = YearlessDateField (
        _('Peak Date')
    )
    radiant_ra = models.FloatField (
        _('Radiant RA')
    )
    radiant_dec = models.FloatField (
        _('Radiant Dec.')
    )
    longitude = models.FloatField (
        _('Celestial Longitude')
    )
    speed = models.PositiveIntegerField (
        _('Avg. Speed'),
        null = True, blank = True,
        help_text = 'km/s'
    )
    zhr = models.PositiveIntegerField (
        _('ZHR'),
        null = True, blank = True
    )
    parent_body = models.CharField (
        _('Parent Body'),
        max_length = 100,
        blank=True, null=True
    )
    notes = models.TextField (
        _('Notes'),
        null = True, blank = True
    )

    def __str__(self):
        return "{}: {} ({})".format(
            self.peak_date,  
            self.name,
            self.parent_body
        )

    @property
    def skyfield_object(self):
        """
        This is handy when pointing at this DSO
        """
        return Star(ra_hours=self.radiant_ra, dec_degrees=self.radiant_dec)

class Asteroid(models.Model):
    """
    Orbital elements are in the brightest_asteroids.txt file.
    Skyfield loads them and uses them from there.
    """
    name = models.CharField (
        _('Name'),
        max_length = 50
    )
    number = models.PositiveIntegerField (
        _('Number')
    )
    diameter = models.CharField (
        _('Diameter'),
        max_length = 50,
        null = True, blank = True,
        help_text = '# or # x # or # x # x #'
    )
    year_of_discovery = models.PositiveIntegerField (
        _('Year of Discovery'),
        null = True, blank = True
    )
    image = models.ImageField (
        _('Image'),
        null = True, blank = True,
        upload_to = 'asteroid_images'
    )
    classification = models.CharField (
        _('Classification'),
        max_length = 10,
        null = True, blank = True
    )
    description = models.TextField (
        _('Description'),
        null = True, blank = True
    )

    ### Magnitude
    h = models.FloatField (
        _('H'),
        help_text = 'absolute magnitude'
    )
    g = models.FloatField (
        _('G'),
        help_text = 'slope parameter'
    )

    @property
    def mpc_lookup_designation(self):
        return "({}) {}".format(self.pk, self.name)
        
    @property
    def mean_diameter(self):
        axes = self.diameter.split('x')
        sum = 0.
        for axis in axes:
            x = float(axis.strip())
            sum += x
        return sum / len(axes)

    @property
    def orbital_period(self):
        return math.sqrt(self.semi_major_axis**3)

    def __str__(self):
        return "{}: {}".format(self.pk, self.name)

    class Meta:
        ordering = ['number']