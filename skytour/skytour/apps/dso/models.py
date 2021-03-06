from django.db import models
from django.db.models import Count, Max, Min, Avg
from django.utils.html import mark_safe
from django.utils.translation import gettext as _
from skyfield.api import Star
from taggit.managers import TaggableManager
from .utils import create_shown_name
from .vocabs import DISTANCE_UNIT_CHOICES
from ..abstract.models import Coordinates, ObjectImage, FieldView, ObservingLog, ObservableObject
from ..abstract.utils import get_metadata
from ..astro.angdist import get_neighbors
from ..astro.transform import get_alt_az
from ..solar_system.utils import get_constellation
from ..utils.models import Constellation, ObjectType
from .pdf import create_pdf_page
from .vocabs import PRIORITY_CHOICES, PRIORITY_COLORS, INT_YES_NO

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
    tags = TaggableManager(blank=True)
    object_class = 'dso'

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

    @property
    def atlas_plate_list(self):
        pp = []
        for p in self.atlasplate_set.all():
            pp.append(str(p.plate_id))
        return ', '.join(pp)

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
        az, alt, airmass = self.alt_az(location, utdt)
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

    @property
    def target_name(self):
        return self.object.shown_name

    @property
    def ra(self):
        return self.object.ra

    @property
    def dec(self):
        return self.object.dec

    @property
    def distance(self):
        return f"{self.object.distance} {self.object.distance_units}"

    def __str__(self):
        return f"{self.ut_datetime}: {self.object_type}: {self.object.shown_name}"
        
    class Meta:
        verbose_name = 'Observation'
        verbose_name_plural = 'Observations'

class DSOList(models.Model):
    """
    Parameters/Features:
        - RA range
        - Type/Subclass
        - pre-seed?
    """
    name = models.CharField (
        _('Name'),
        max_length = 100
    )
    description = models.TextField (
        _('Description'),
        null = True, blank = True
    )
    dso = models.ManyToManyField (DSO)
    tags = TaggableManager(blank=True)
    show_on_plan = models.PositiveIntegerField (
        _('On Plan PDF'),
        choices = INT_YES_NO,
        default = 1,
        help_text = 'Set to YES/1 to add this to a PDF plan'
    )

    def get_absolute_url(self):
        return '/dso/list/{}'.format(self.pk)

    @property
    def mid_ra(self):
        """
        Ugh - this won't work for things straddling 0h RA.
        """
        avg = self.dso.aggregate(avg=Avg('ra'))['avg']
        min_ra, max_ra = self.ra_range
        if max_ra - min_ra > 12:
            avg = avg - 12.
        if avg < 0:
            avg += 24.
        return avg
    
    @property
    def mid_dec(self):
        avg = self.dso.aggregate(avg=Avg('dec'))['avg']
        return avg

    @property
    def ra_range(self):
        ra_min = None
        ra_max = None
        for dso in self.dso.all():
            if ra_min is None or dso.ra < ra_min:
                ra_min = dso.ra
            if ra_max is None or dso.ra > ra_max:
                ra_max = dso.ra
        return (ra_min, ra_max)

    @property
    def dec_range(self):
        dec_min = None
        dec_max = None
        for dso in self.dso.all():
            if dec_min is None or dso.dec < dec_min:
                dec_min = dso.dec
            if dec_max is None or dso.dec > dec_max:
                dec_max = dso.dec
        return (dec_min, dec_max)

    @property
    def dso_count(self):
        return self.dso.count()

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'DSO List'
        verbose_name_plural = 'DSO Lists'
        ordering = ['-pk']

class AtlasPlate(models.Model):
    """
    TODO: Bright Star Lists
    TODO: Double Stars?
    TODO: "Special" plates for things like the LMC/SMC/Virgo, etc. - These will need a different FOV, or 
        might be split up into sections...   Need to research.
    """
    plate_id = models.PositiveIntegerField(_('Plate ID'), unique=True)
    slug = models.SlugField(unique=True)
    center_ra = models.FloatField(_('Center RA'))
    center_dec = models.FloatField(_('Center Dec'))
    radius = models.FloatField(_('Radius'), default=20.0)
    tags = TaggableManager(blank=True)
    dso = models.ManyToManyField(DSO, blank=True)
    constellation = models.ManyToManyField(Constellation, blank=True)

    @property
    def center_constellation(self):
        lookup = get_constellation(self.center_ra, self.center_dec)
        constellation = Constellation.objects.filter(abbreviation__iexact=lookup['abbr']).first()
        return constellation
    center_constellation.fget.short_description = 'Con.'

    @property
    def constellation_list(self):
        cc = []
        for c in self.constellation.all():
            cc.append(c.abbreviation)
        return ', '.join(cc)

    @property
    def dso_count(self):
        return self.dso.count()

    @property
    def plate_title(self):
        return f"Plate {self.plate_id}: ({self.center_ra:.2f}h {self.center_dec}??) in {self.center_constellation}"

    @property
    def plate_images(self):
        """
        Create a dict of all available atlas plate image renditions.
        There should be 4:
            default = black-on-white, symbols
            shapes = black-on-white, shapes
            reversed = white-on-black, symbols
            shapesreversed = white-on-black, shapes
        """
        vv = self.atlasplateversion_set.all()
        d = {}
        for v in vv:
            if v.shapes:
                k = 'shapesreversed' if v.reversed else 'shapes'
            else:
                k = 'reversed' if v.reversed else 'default'
            d[k] = v
        return d

    def save(self, *args, **kwargs):
        self.slug = self.plate_id
        super(AtlasPlate, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return '/atlas/{}'.format(self.plate_id)

    def __str__(self):
        return f"Plate {self.plate_id}"

    class Meta:
        verbose_name = 'Atlas Plate'
        verbose_name_plural = 'Atlas Plates'
        ordering = ['plate_id']

class AtlasPlateVersion(models.Model):
    plate = models.ForeignKey(AtlasPlate, on_delete=models.CASCADE)
    shapes = models.BooleanField(_('Shapes'), default=False)
    reversed = models.BooleanField('Reversed', default=False)
    image = models.ImageField(
        _('Plate'),
        upload_to = 'atlas_images',
        null = True, blank = True
    )

    def plate_tag(self):
        return mark_safe(u'<img src="%s" width=500>' % self.image.url)

    def __str__(self):
        return f"{self.plate.plate_id}: shapes={self.shapes} reversed={self.reversed}"

class MilkyWay(models.Model):
    """
    Each row is a data point along a segment/contour of a particular level.
    There are >1 segments of each.
    """
    contour = models.PositiveIntegerField (_('Level'),help_text = '1 to 5, 5 being the most intense')
    segment = models.PositiveIntegerField (_('Segment #'),)
    longitude = models.FloatField (_('Longitude'),)
    ra = models.FloatField(_('R.A. 2000'))
    dec = models.FloatField(_('Dec. 2000'))

class AtlasPlateConstellationAnnotation(models.Model):
    """
    Each row is a position for a label on an Atlas Plate for a Constellation
    """
    plate = models.ForeignKey(AtlasPlate, on_delete=models.CASCADE)
    constellation = models.ForeignKey(Constellation, on_delete=models.CASCADE)
    ra = models.FloatField(_('R.A.'))
    dec = models.FloatField(_('Dec.'))



