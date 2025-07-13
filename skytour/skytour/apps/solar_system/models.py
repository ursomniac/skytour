import datetime as dt
from io import StringIO
import math
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)
import pandas as pd
import json
from django.db import models
from django.utils.html import mark_safe
from django.utils.translation import gettext as _
from djangoyearlessdate.models import YearlessDateField
from jsonfield import JSONField
from skyfield.api import Star
from ..abstract.models import ObservingLog, ObservableObject, LibraryAbstractImage, WikipediaPage, WikipediaPageObject
from ..abstract.utils import get_metadata
from ..abstract.vocabs import YES, NO, YES_NO
from ..utils.text import replace_greek_letters
from .asteroids import get_asteroid_object, lookup_asteroid_object, create_asteroid_dict
from .comets import get_comet_object, get_comet_period
from .planets import get_mean_orbital_elements
from .vocabs import STATUS_CHOICES

class Planet(ObservableObject, WikipediaPageObject):
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

    planet_map = models.ImageField( # This is only used for Mars and Jupiter
        _('Planet Map'),
        null=True, blank=True,
        upload_to='planet_maps'
    )
    object_class = 'planet'
    detail_view = 'planet-detail'

    @property
    def instance_id(self):
        return self.slug
    
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
    
    @property
    def orbital_elements(self):
        return get_mean_orbital_elements(self.name)
    
    @property
    def orbital_period(self):
        a = self.orbital_elements['semimajor_axis']
        p = math.sqrt(a**3)
        return p
    
    @property
    def orbital_period_days(self):
        return self.orbital_period * 365.25
    
    @property
    def num_library_images(self):
        return self.image_library.count()
    
    @property
    def library_image(self):
        return self.image_library.order_by('order_in_list').first() # returns None if none
    
    @property
    def num_slideshow_images(self):
        return self.image_library.filter(use_in_carousel=True).count()
    
    @property
    def bsp_file(self):
        return f"generated_data/{self.load}"
    
    @property
    def default_wikipedia_name(self):
        return f"{self.name}_(planet)"
    
    def get_absolute_url(self):
        return '/planet/{}'.format(self.slug)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['semi_major_axis']

class PlanetLibraryImage(LibraryAbstractImage):
    object = models.ForeignKey(
        Planet,
        on_delete = models.CASCADE,
        related_name = 'image_library'
    )
    ut_datetime = models.DateTimeField()

    def __str__(self):
        return self.object.name
    
    class Meta:
        verbose_name = 'Planet Library Image'
        verbose_name = 'Planet Library Images'


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
    M:1 between observations and Planet.
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

class PlanetWiki(WikipediaPage):
    object = models.OneToOneField(
        Planet, 
        on_delete=models.CASCADE,
        primary_key = True,
        related_name = 'wiki'
    )

class MoonObservation(ObservingLog):
    object_type = 'Moon'

    @property
    def target_name(self):
        return 'Moon'

    def __str__(self):
        return f"{self.ut_datetime}: Moon"

    class Meta:
        verbose_name = 'Moon Observation'
        verbose_name_plural = 'Moon Observations'


SHOWER_IMPORTANCE = (
    ('Major', 'Major'),
    ('Minor', 'Minor'),
    ('Sporadic', 'Sporadic')
)
class MeteorShower(WikipediaPageObject, models.Model):

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
    intensity = models.CharField (
        _('Intensity'),
        max_length = 20,
        choices = SHOWER_IMPORTANCE,
        default = 'Major'
    )
    radiant_map = models.ImageField (
        _('Radiant Map'),
        upload_to='meteor_map',
        null = True, blank = True
    )

    def get_absolute_url(self):
        return '/meteor/{}'.format(self.pk)

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

    @property
    def default_wikipedia_name(self):
        name = replace_greek_letters(self.name)
        return name
    
    class Meta:
        ordering = ['peak_date']
    
class MeteorShowerWiki(WikipediaPage):
    object = models.OneToOneField(
        MeteorShower, 
        on_delete=models.CASCADE,
        primary_key = True,
        related_name = 'wiki'
    )

class Asteroid(ObservableObject, WikipediaPageObject):
    """
    Orbital elements are in the brightest_asteroids.txt file.
    Skyfield loads them and uses them from there.
    """
    name = models.CharField (
        _('Name'),
        max_length = 50,
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
    always_include = models.BooleanField (
        _('Always Include'),
        default = False,
        help_text = 'Override magnitude limit, e.g., for Pluto'
    )
    est_brightest = models.FloatField (
        _('Estimated Brightest'),
        null = True, blank = True
    )
    mpc_json = JSONField(
        _('MPC as JSON'),
        null=True, blank=True,
        help_text='JSON object constructed from HyperLeda lookup'
    )

    object_class = 'asteroid'
    detail_view = 'asteroid-detail'

    @property
    def instance_id(self):
        return self.slug
    
    @property
    def mean_diameter(self):
        axes = self.diameter.split('x')
        sum = 0.
        for axis in axes:
            x = float(axis.strip())
            sum += x
        return sum / len(axes)
    
    @property
    def is_dwarf_planet(self):
        DWARF_PLANETS = [134340, 136199, 136108, 136472] # ignore Ceres for now
        return self.number in DWARF_PLANETS

    @property
    def orbital_period(self):
        if self.mpc_object_dict['semimajor_axis_au']:
            a = float(self.mpc_object_dict['semimajor_axis_au'])
            return math.sqrt(a**3)
        return None

    @property
    def full_name(self):
        return "{}: {}".format(self.number, self.name)
    
    @property
    def num_library_images(self):
        return self.image_library.count()
    
    @property
    def library_image(self):
        return self.image_library.order_by('order_in_list').first() # returns None if none
    
    @property
    def num_slideshow_images(self):
        return self.image_library.filter(use_in_carousel=True).count()
    
    @property
    def mag_h(self):
        try:
            return float(self.mpc_object['magnitude_H'])
        except:
            return None
    
    @property
    def mag_g(self):
        try:
            return float(self.mpc_object['magnitude_G'])
        except:
            return None
    
    @property
    def mpc_lookup_designation(self):
        return "({}) {}".format(self.number, self.name)
        
    @property
    def mpc_object(self):
        try:
            return pd.read_json(StringIO(self.mpc_json), typ='series')
        except: # Keep for now TODO: deprecate!
            return get_asteroid_object(self) # will return None if not in short-list
    
    @property
    def mpc_object_dict(self):
        return self.mpc_object.to_dict()
    
    @property
    def default_wikipedia_name(self):
        if self.is_dwarf_planet:
            return f"{self.name}_(dwarf planet)"
        return f"{self.number} {self.name}"
    
    def get_absolute_url(self):
        return '/asteroid/{}'.format(self.slug)
    
    def save(self, *args, **kwargs):
        mpc = None
        print("SAVE: slug = ", self.slug)
        print("SAVE MPC: ", self.mpc_json)
        if self.slug is None or self.slug == '':
            words = [str(self.number)] + self.name.split(' ')
            slug = '-'.join(words)
            self.slug = slug.lower()

        if self.mpc_json is None:            
            #mpc = get_asteroid_object(self) # Deprecate - but faster
            if mpc is None or mpc.empty:
                mpc = lookup_asteroid_object(self.mpc_lookup_designation)
            if mpc is not None and not mpc.empty:
                d = create_asteroid_dict(mpc)
                print("D: ", d)
                j = json.dumps(d)
                print("J: ", j)
                self.mpc_json = j

        print("FINAL: slug = ", self.slug)
        print("FINAL MPC = ", self.mpc_json)
        super(Asteroid, self).save(*args, **kwargs)

    def __str__(self):
        return "{}: {}".format(self.number, self.name)

    class Meta:
        ordering = ['number']

class AsteroidLibraryImage(LibraryAbstractImage):
    object = models.ForeignKey(
        Asteroid,
        on_delete = models.CASCADE,
        related_name = 'image_library'
    )
    ut_datetime = models.DateTimeField()

    def __str__(self):
        return self.object.full_name
    
    class Meta:
        verbose_name = 'Asteroid Library Image'
        verbose_name = 'Asteroid Library Images'

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

class AsteroidWiki(WikipediaPage):
    object = models.OneToOneField(
        Asteroid, 
        on_delete=models.CASCADE,
        primary_key = True,
        related_name = 'wiki'
    )


class Comet(ObservableObject, WikipediaPageObject):

    name = models.CharField(
        _('Name'),
        max_length = 50,
        help_text = 'MPC format, e.g. 1P/Halley, C/2025 F2'
    )
    status = models.PositiveIntegerField (
        _('Status'),
        choices = STATUS_CHOICES,
        default = 1,
        help_text = 'Include in Cookie'
    )
    mag_offset = models.FloatField (
        _('Mag Offset'),
        default = 0.,
        help_text='Offset Mag if esp. brighter/dimmer than predicted'
    )
    light_curve_url = models.URLField (
        _('Light Curve URL'),
        null = True, blank = True,
        help_text='Comet page at http://www.aerith.net'
    )
    light_curve_graph_url = models.URLField (
        _('Light Curve Graph URL'),
        null = True, blank = True,
        help_text = 'URL for the light curve at http://www.aerith.net'
    )
    override_limits = models.PositiveIntegerField(
        choices = YES_NO,
        default = NO,
        help_text = 'Force adding to cookie, regardless of magnitude'
    )
    perihelion_date = models.DateField ( # Calculated on save()
        _('Peri.'),
        null = True, blank = True,
        help_text = 'Auto calcualted from elements'
    )
    object_class = 'comet'
    detail_view = 'comet-detail'
    
    @property
    def instance_id(self):
        return self.pk

    @property
    def num_library_images(self):
        return self.image_library.count()
    
    @property
    def library_image(self):
        return self.image_library.order_by('order_in_list').first() # returns None if none

    @property
    def num_slideshow_images(self):
        return self.image_library.filter(use_in_carousel=True).count()
    
    @property
    def test_light_curve_graph(self):
        if self.light_curve_url is None:
            return None
        pieces = self.light_curve_url.split('/')
        x = self.light_curve_url.replace(pieces[-1], 'mag.gif')
        return mark_safe(f'<img src="{x}" width=500>')
    
    @property
    def mpc_object(self):
        return get_comet_object(self)
    
    @property
    def mpc_object_dict(self):
        return self.mpc_object.to_dict()
    
    @property
    def get_perihelion_date(self):
        try:
            object = self.mpc_object   
            year = object['perihelion_year']
            month = object['perihelion_month']
            day = int(object['perihelion_day'])
            pdate = dt.date(year, month, day)
        except:
            pdate = None
        return pdate
    
    @property
    def comet_period(self):
        return get_comet_period(self.mpc_object)
    
    @property
    def status_bool(self):
        return 'Active' if self.status else 'Not Active'
    
    @property
    def override_limits_bool(self):
        return 'Yes' if self.override_limits else 'No'
    
    @property
    def default_wikipedia_name(self):
        return f"{self.name}"

    def get_absolute_url(self):
        return '/comet/{}'.format(self.pk)
    
    def save(self, *args, **kwargs):
        self.perihelion_date = self.get_perihelion_date
        super(Comet, self).save(*args, **kwargs)

    def __str__(self):
        return f"{self.name}"
    
    class Meta:
        ordering = ['perihelion_date']

class CometLibraryImage(LibraryAbstractImage):
    object = models.ForeignKey(
        Comet,
        on_delete = models.CASCADE,
        related_name = 'image_library'
    )
    ut_datetime = models.DateTimeField()

    def __str__(self):
        return self.object.name
    
    class Meta:
        verbose_name = 'Comet Library Image'
        verbose_name = 'Comet Library Images'


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

class CometWiki(WikipediaPage):
    object = models.OneToOneField(
        Comet, 
        on_delete=models.CASCADE,
        primary_key = True,
        related_name = 'wiki'
    )


class PlanetMoon(models.Model):
    name = models.CharField(
        _('Name'),
        max_length=50,
    )
    planet = models.ForeignKey(Planet, on_delete=models.CASCADE)
    planet_index = models.PositiveIntegerField(
        _('Index')
    )
    radius = models.FloatField(
        _('Radius'),
        help_text = 'km'
    )
    major_axis = models.FloatField(
        _('Dist. from Planet'),
        help_text = 'km',
        null = True, blank = True
    )
    albedo = models.FloatField(
        _('Albedo')
    )
    h = models.FloatField(
        _('H'),
        help_text = 'abs. mag'
    )
    g = models.FloatField(
        ('G'),
        default = 0.15,
        help_text = 'slope parameter'
    )
    period = models.FloatField(
        ('Period'),
        help_text = ('hours')
    )
    use_in_modeling = models.PositiveIntegerField(
        choices = YES_NO,
        default = NO
    )

    class Meta:
        verbose_name = 'Planetary Satellite'
        verbose_name_plural = 'Planetary Satellites'

    def __str__(self):
        return self.name

    @property
    def period_in_days(self):
        return self.period / 24.

    @property
    def apparent_magnitude(self, earth_dist, sun_dist):
        m = self.h + 5 * math.log10(earth_dist * sun_dist) - self.g
        return m