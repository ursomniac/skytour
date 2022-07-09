import math
from django.db import models
from django.utils.translation import gettext as _
from djangoyearlessdate.models import YearlessDateField
from skyfield.api import Star
from ..abstract.models import ObservingLog, ObservableObject
from ..abstract.utils import get_metadata
from .vocabs import STATUS_CHOICES

class Planet(ObservableObject):
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
    object_class = 'planet'

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

class PlanetObservation(ObservingLog):
    """
    M:1 between observation records and DSOs.
    So a separate one of these for model?   That gets away from
    dealing with GFKs...
    """
    object = models.ForeignKey(Planet,
        on_delete = models.CASCADE,
        related_name = 'observations'
    )
    object_type = 'Planet'
    url_path = 'planet-detail'

    @property
    def observation_metadata(self):
        return get_metadata(self)

    @property
    def target_name(self):
        return self.object.name

    def __str__(self):
        return f"{self.ut_datetime}: {self.object_type}: {self.object.name}"

    class Meta:
        verbose_name = 'Observation'
        verbose_name_plural = 'Observations'

class MoonObservation(ObservingLog):
    object_type = 'moon'

    @property
    def target_name(self):
        return 'Moon'

    def __str__(self):
        return f"{self.ut_datetime}: Moon"

    class Meta:
        verbose_name = 'Moon Observation'
        verbose_name_plural = 'Moon Observations'

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

class Asteroid(ObservableObject):
    """
    Orbital elements are in the brightest_asteroids.txt file.
    Skyfield loads them and uses them from there.
    """
    name = models.CharField (
        _('Name'),
        max_length = 50
    )
    slug = models.SlugField (
        _('Slug')
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

    est_brightest = models.FloatField (
        _('Estimated Brightest'),
        null = True, blank = True
    )
    object_class = 'asteroid'

    @property
    def mpc_lookup_designation(self):
        return "({}) {}".format(self.number, self.name)
        
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

    @property
    def full_name(self):
        return "{}: {}".format(self.number, self.name)

    def get_absolute_url(self):
        return '/asteroid/{}'.format(self.slug)

    def __str__(self):
        return "{}: {}".format(self.number, self.name)

    class Meta:
        ordering = ['number']

class AsteroidObservation(ObservingLog):
    """
    M:1 between observation records and DSOs.
    So a separate one of these for model?   That gets away from
    dealing with GFKs...
    """
    object = models.ForeignKey(Asteroid,
        on_delete = models.CASCADE,
        related_name = 'observations'
    )
    object_type = 'Asteroid'
    url_path = 'asteroid-detail'

    @property
    def observation_metadata(self):
        return get_metadata(self)

    @property
    def target_name(self):
        return self.object.name

    def __str__(self):
        return f"{self.ut_datetime}: {self.object_type}: {self.object.name}"

    class Meta:
        verbose_name = 'Observation'
        verbose_name_plural = 'Observations'

class Comet(ObservableObject):

    name = models.CharField(
        _('Name'),
        max_length = 50
    )
    status = models.PositiveIntegerField (
        _('Status'),
        choices = STATUS_CHOICES,
        default = 1
    )
    mag_offset = models.FloatField (
        _('Mag Offset'),
        default = 0.
    )
    object_class = 'comet'
        
    def get_absolute_url(self):
        return '/comet/{}'.format(self.pk)

    def __str__(self):
        return f"{self.pk}: {self.name}"

class CometObservation(ObservingLog):
    """
    M:1 between observation records and DSOs.
    So a separate one of these for model?   That gets away from
    dealing with GFKs...
    """
    object = models.ForeignKey(Comet,
        on_delete = models.CASCADE,
        related_name = 'observations'
    )
    object_type = 'Comet'
    url_path = 'comet-detail'
    
    @property
    def observation_metadata(self):
        return get_metadata(self)

    @property
    def target_name(self):
        return self.object.name

    def __str__(self):
        return f"{self.ut_datetime}: {self.object_type}: {self.object.name}"

    class Meta:
        verbose_name = 'Observation'
        verbose_name_plural = 'Observations'