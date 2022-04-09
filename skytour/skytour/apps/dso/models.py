from django.db import models
from django.utils.html import mark_safe
from django.utils.translation import gettext as _
from skyfield.api import Star
from .utils import create_shown_name
from .vocabs import DISTANCE_UNIT_CHOICES
from ..abstract.models import Coordinates, ObjectImage, FieldView, ObservingLog, ObservableObject
from ..abstract.utils import get_metadata
from ..astro.angdist import get_neighbors
from ..astro.transform import get_alt_az
from ..utils.models import Constellation, ObjectType
from .pdf import create_pdf_page

PRIORITY_CHOICES = [
    ('Highest', 'Highest'),
    ('High', 'High'),
    ('Medium', 'Medium'),
    ('Low', 'Low'),
    ('None', 'None')
]
PRIORITY_COLORS = {
    'Highest': '#f00',
    'High': '#c90',
    'Medium': '#090',
    'Low': '#096',
    'None': '#ccc'
}
INT_YES_NO = (
    (0, 'No'),
    (1, 'Yes')
)

class DSO(Coordinates, FieldView, ObservableObject):
    """
    Basically everything we want:
        Name and Aliases
            - botn are in the Object Alias abstract class:
                the primary name is in this model, the other
                is in a FK to this model from DSOAlias.
        Images
        Field View (https://astronomy.tools/calculators/field_of_view/)
    """
    catalog = models.ForeignKey('utils.Catalog', on_delete = models.CASCADE)
    id_in_catalog = models.CharField (
        _('ID'),
        max_length = 24
    )
    shown_name = models.CharField (
        _('Shown Name'),
        max_length = 100,
        null = True, blank = True
    )
    nickname = models.CharField(
        _('Nickname'),
        max_length = 200,
        null = True, blank = True
    )
    constellation = models.ForeignKey (Constellation, on_delete=models.PROTECT)
    object_type = models.ForeignKey(ObjectType, on_delete=models.PROTECT)
    morphological_type = models.CharField (
        _('Morphological Type'),
        max_length = 20,
        null = True, blank = True,
        help_text = 'Gal Type, GC Class, etc.'
    )
    magnitude = models.FloatField (
        _('Mag.'),
        null = True, blank = True
    )
    angular_size = models.CharField (
        _('Angular Size'),
        max_length = 50,
        null = True, blank = True,
        help_text = 'single or double dimension, e.g., 8\' by 12\''
    )
    surface_brightness = models.FloatField (
        _('Surface Brightness'),
        null = True, blank = True
    )
    contrast_index = models.FloatField (
        _('Contrast Index'),
        null = True, blank = True
    )
    distance = models.FloatField (
        _('Distance'),
        null = True, blank = True,
    )
    distance_units = models.CharField (
        _('Distance Unit'),
        max_length = 10,
        choices = DISTANCE_UNIT_CHOICES,
        null = True, blank = True
    )
    notes = models.TextField (
        _('Notes'),
        null = True, blank = True
    )

    finder_chart = models.ImageField (
        _('Finder Chart'),
        upload_to = 'finder_chart/',
        null = True, blank = True
    )

    dso_finder_chart = models.ImageField (
        _('DSO Finder Chart'),
        upload_to = 'dso_finder_chart',
        null = True, blank = True
    )
    priority = models.CharField (
        _('Priority'),
        max_length = 20,
        choices = PRIORITY_CHOICES,
        null = True, blank = True
    )
    show_on_skymap = models.PositiveIntegerField (
        _('Show on Skymap'),
        default = 0,
        choices = INT_YES_NO
    )

    # From Stellarium DSO model and SIMBAD
    orientation_angle = models.PositiveIntegerField (
        _('Orientation Angle'),
        null = True, blank = True,
        help_text = 'Degrees'
    )
    major_axis_size = models.FloatField (
        _('Size: Major Axis'),
        null = True, blank = True,
        help_text = 'arcmin'
    )
    minor_axis_size = models.FloatField (
        _('Size: Minor Axis'),
        null = True, blank = True,
        help_text = 'arcmin'
    )

    pdf_page = models.FileField (
        _('PDF Page'),
        null = True, blank = True,
        upload_to = 'dso_pdf'
    )

    @property
    def alias_list(self):
        aliases = []
        for alias in self.aliases.all():
            aliases.append(alias.shown_name)
        return ', '.join(aliases)

    @property
    def skyfield_object(self):
        """
        This is handy when pointing at this DSO
        """
        return Star(ra_hours=self.ra_float, dec_degrees=self.dec_float)

    @property
    def nearby_dsos(self):
        return get_neighbors(self)

    @property
    def priority_color(self):
        if self.priority:
            return PRIORITY_COLORS[self.priority]
        return '#666'

    def finder_chart_tag(self):
        """
        This makes the uploaded finder chart appear on the Admin page.
        """
        return mark_safe(u'<img src="%s" width=500>' % self.finder_chart.url)

    def dso_finder_chart_tag(self):
        return mark_safe(u'<img src="%s" width=500>' % self.dso_finder_chart.url)

    def alt_az(self, location, utdt):
        """
        Get my Alt/Az at a given UTDT.
        """
        return get_alt_az(utdt, location.latitude, location.longitude, self.ra, self.dec)

    def object_is_up(self, location, utdt, min_alt=0.):
        """
        This is still used when creating an observing plan.
        Tests if a DSO is observable within a UTDT window.
        """
        az, alt = self.alt_az(location, utdt)
        if alt > min_alt:
            return True
        return False

    def get_absolute_url(self):
        return '/dso/{}'.format(self.pk)

    def save(self, *args, **kwargs):
        self.ra = self.ra_float # get from property
        self.dec = self.dec_float # get from property
        self.ra_text = self.format_ra # get from property
        self.dec_text = self.format_dec # get from property
        self.shown_name = create_shown_name(self)
        # Generate a DSO finder chart if one doesn't exist
        # Except you can't - it crashes everything, UNLESS
        # you run the code in it's own thread.  Why?  Who knows?
        # UPDATE: 2 Jan 2022 --- this might actually work now.
        fn = create_pdf_page(self)
        self.pdf_page.name = fn
        super(DSO, self).save(*args, **kwargs)
        
    class Meta:
        verbose_name = 'Deep Sky Object'
        verbose_name_plural = 'DSOs'
        ordering = ['ra', 'dec']

    def __str__(self):
        return self.shown_name

class DSOAlias(models.Model):
    """
    This has all of the aliases for a DSO.
    There's a slight precedence in catalogs:
        - Messier
        - Caldwell
        - NGC
        - IC
        - Herschel 400
    so that M 52 = NGC 7654 = Cr 455 = Mel 243.
    Several search functions check aliases, so you SHOULD always reach the
    desired object.
    """
    object = models.ForeignKey(DSO, 
        on_delete=models.CASCADE,
        related_name='aliases'
    )
    catalog = models.ForeignKey('utils.Catalog', on_delete = models.CASCADE)
    id_in_catalog = models.CharField (
        _('ID'),
        max_length = 24
    )
    shown_name = models.CharField (
        _('Shown Name'),
        max_length = 100,
        null = True, blank = True
    )
    class Meta:
        verbose_name = 'Alias'
        verbose_name_plural = 'Aliases'

    def __str__(self):
        return self.shown_name

    def save(self, *args, **kwargs):
        self.shown_name = create_shown_name(self)
        super(DSOAlias, self).save(*args, **kwargs)

class DSOImage(ObjectImage):
    """
    M:1 between uploaded images and a DSO
    """
    object = models.ForeignKey(DSO,
        on_delete = models.CASCADE,
        related_name = 'images'
    )
    class Meta:
        verbose_name = 'Image'
        verbose_name_plural = 'Images'

class DSOObservation(ObservingLog):
    """
    M:1 between observation records and DSOs.
    So a separate one of these for model?   That gets away from
    dealing with GFKs...
    """
    object = models.ForeignKey(DSO,
        on_delete = models.CASCADE,
        related_name = 'observations'
    )

    # these probably should be class parameters.
    object_type = 'DSO'
    url_path = 'dso-detail'

    @property
    def observation_metadata(self):
        return get_metadata(self)
        
    def __str__(self):
        return f"{self.ut_datetime}: {self.object_type}: {self.object.shown_name}"
        
    class Meta:
        verbose_name = 'Observation'
        verbose_name_plural = 'Observations'

