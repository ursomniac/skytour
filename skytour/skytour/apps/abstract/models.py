import datetime
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.utils.html import mark_safe
from django.utils.translation import gettext as _
from ..astro.time import utc_now
from ..observe.models import ObservingLocation
from ..session.models import ObservingSession
from ..site_parameter.helpers import find_site_parameter
from ..tech.models import Telescope, Eyepiece, Filter
from ..astro.transform import get_cartesian
from .vocabs import (
    IMAGE_PROCESSING_STATUS_OPTIONS,
    IMAGE_ORIENTATION_CHOICES,
    IMAGE_CROPPING_OPTIONS,
    #
    YES_NO, YES, NO
)

##### Abstract Models
class Coordinates(models.Model):
    """
    Abstract RA/Dec coordinates
        - stores HMS and DMS separately
        - has floating values calculated in an model instance save()
    """
    ra_h = models.PositiveIntegerField ( 
        _('RA: hr'),
        validators=[MaxValueValidator(23)]
    )
    ra_m = models.PositiveIntegerField (
        _('min'),
        validators=[MaxValueValidator(59)]
    )
    ra_s = models.FloatField (
        _('sec'),
        validators=[
            MinValueValidator(0.000),
            MaxValueValidator(59.9999999)
        ],
        null = True, blank = True
    )
    # These are both set in the save()
    ra = models.FloatField (
        _('R.A.'),
        null = True, blank = True
    )
    ra_text = models.CharField (
        _('R.A. Text'),
        max_length = 16,
        null = True, blank = True
    )
    ### Dec.
    dec_sign = models.CharField (
        _('Dec: Sign'),
        max_length = 1,
        choices = ( ('+', '+'), ('-', '-') )
    )
    dec_d = models.IntegerField (
        _('deg'),
        validators=[
            MinValueValidator(0),
            MaxValueValidator(89)
        ]
    )
    dec_m = models.PositiveIntegerField (
        _('min'),
        validators = [MaxValueValidator(59)]
    )
    dec_s = models.FloatField (
        _('sec'),
        validators = [
            MinValueValidator(0.000),
            MaxValueValidator(59.9999999)
        ],
        null = True, blank = True
    )
    # These are both set in the save()
    dec = models.FloatField (
        _('Dec.'),
        null = True, blank = True
    )
    dec_text = models.CharField (
        _('Dec. Text'),
        max_length = 16,
        null = True, blank = True
    )

    @property
    def ra_float(self):
        x = self.ra_h + self.ra_m/60. 
        if self.ra_s:
            x += self.ra_s/3600. 
        return x
    
    @property
    def ra_deg_float(self):
        return self.ra_float * 15.
    
    @property
    def dec_float(self):
        x = self.dec_d + self.dec_m/60. 
        if self.dec_s: 
            x += self.dec_s/3600. 
        if self.dec_sign == '-':
            x *= -1.0
        return x

    @property
    def format_ra(self):
        return "{:02d}h {:02d}m {:05.2f}s".format(
            self.ra_h, self.ra_m, self.ra_s
        )

    @property
    def format_dec(self):
        return u"{}{:02d}° {:02d}\' {:05.2f}\"".format(
            self.dec_sign, self.dec_d, self.dec_m, self.dec_s
        )

    @property
    def short_ra_dec(self):
        rah = int(self.ra)
        ram = (self.ra - rah) * 60.
        des = '-' if self.dec < 0 else '+'
        dex = abs(self.dec) + 0.00015 # rounding
        ded = int(dex)
        dem = (dex - ded) * 60.
        return f"{rah:02d}h{ram:04.1f}m {des}{ded:02d}°{dem:04.1f}\'"
    
    @property
    def get_xyz(self):
        """
        Convert RA/Dec to XYZ
        """
        return get_cartesian(self.ra_float, self.dec_float, ra_dec = True)

    class Meta:
        abstract = True


class ObjectImage(models.Model):
    """
    Abstract model for images (external) attached to objects.
    """
    image = models.ImageField (
        _('Image'),
        upload_to = 'object_image/'
    )
    notes = models.TextField (
        _('Notes'),
        blank = True, null = True
    )
    caption = models.TextField (
        _('Caption'), null=True, blank=True
    )
    order_in_list = models.PositiveIntegerField (
        _('Order'),
        default = 1
    )

    def object_image_tag(self):
        return mark_safe(u'<img src="%s" width=500>' % self.image.url)

    class Meta:
        abstract = True

class LibraryAbstractImage(ObjectImage):
    """
    Abstract class for user-created DSO, Planet, Asteroid, Comet images
    """
    # If True - is shown on the "Library Panel" (for square images)
    use_in_carousel = models.PositiveIntegerField (
        _('Use in Slideshow'),
        choices = YES_NO,
        default = YES,
        help_text = 'Set to YES/1 show on the image carousel'
    )
    # If True - is sown on the "Full-Sized View Panel" (for landscape images)
    use_as_map = models.PositiveIntegerField (
        _('Use in Map Panel'),
        choices = YES_NO,
        default = NO,
        help_text = 'Set to YES/1 show on the map panel'
    )
    exposure = models.FloatField (
        _('Image Exposure'),
        null = True, blank = True,
        help_text = 'in floating minutes'
    )

    image_orientation = models.CharField (
        _('Image Orientation'),
        max_length = 20,
        blank = True, null = True,
        choices = IMAGE_ORIENTATION_CHOICES
    )

    image_processing_status = models.CharField (
        _('Image Processing Status'),
        max_length = 20,
        blank = True, null = True,
        choices = IMAGE_PROCESSING_STATUS_OPTIONS
    )

    image_cropping = models.CharField (
        _('Image Cropping'),
        max_length = 20,
        blank = True, null = True,
        choices = IMAGE_CROPPING_OPTIONS
    )

    telescope = models.ForeignKey (
        Telescope,
        null = True, blank = True,
        on_delete = models.PROTECT
    )
    
    @property
    def caption(self):
        x = ''
        if self.telescope is not None:
            x += f"{self.telescope.name}: "
        x += self.ut_datetime.strftime('%Y-%m-%d %H:%M UT')
        if self.exposure is not None:
            x += f', {self.exposure}min'
        if self.image_processing_status not in [None, 'None']:
            x += f', {self.get_image_processing_status_display()}'
        return x
    
    @property
    def panel_list(self):
        panel=[]
        if self.use_in_carousel:
            panel.append('panel')
        if self.use_as_map:
            panel.append('map')
        return panel
    
    def __str__(self):
        panel_str = '+'.join(self.panel_list)
        pf = None
        if panel_str != '':
            pf = f"[{panel_str} - {self.order_in_list:3d}]"
        return  f"{self.object}: {pf} {self.ut_datetime} {self.telescope} {self.image_orientation} {self.image_processing_status}"
    
    class Meta:
        abstract = True


class ObservingLog(models.Model):
    """
    Generic observation.
    """
    session = models.ForeignKey(ObservingSession, null=True, on_delete=models.CASCADE)
    ut_datetime = models.DateTimeField (
        _('UTDT of Obs.'),
        default = utc_now, 
        help_text = 'Date/Time (UT)'
    )
    # telescope
    telescope = models.ForeignKey (
        _(Telescope),
        default = 1,
        on_delete = models.CASCADE
    )
    # Eyepiece(s)
    eyepieces = models.ManyToManyField (Eyepiece, blank=True)
    # Filter(s)
    filters = models.ManyToManyField (Filter, blank=-True)
    
    # TODO V2.x: deal with sensors!

    # Ugh you need location!
    location = models.ForeignKey (
        ObservingLocation,
        default = ObservingLocation.get_default_location().pk,
        on_delete = models.CASCADE,
        limit_choices_to = {'status__in': ['Active', 'Provisional']}
    )

    # Filter(s)
    notes = models.TextField (
        _('Notes'),
        null = True, blank = True
    )

    @property
    def eyepiece_list(self):
        elist = [e.short_name for e in self.eyepieces.all()]
        return ', '.join(elist)

    @property
    def filter_list(self):
        flist = [f.short_name for f in self.filters.all()]
        return ', '.join(flist)

    class Meta:
        abstract = True

class ObservableObject(models.Model):
    """
    Properties for observable objects:
        1. Last Observed
    """
    @property
    def last_observed(self):
        obs = self.observations.order_by('-ut_datetime').first()
        if obs is None:
            return None
        return obs.ut_datetime
    
    # TODO: Deprecate eventually
    @property
    def reimage_flag(self):
        if self.number_of_observations < 1:
            return False
        if self.num_library_images < 1:
            return False
        x = datetime.datetime(2023, 12, 1, 0, 0, 0)
        x = x.replace(tzinfo=datetime.timezone.utc)
        if self.last_observed < x:
            return True
        return False
    
    # TODO: Deprecate eventually
    @property
    def need_to_image_flag(self):
        if self.number_of_observations < 1:
            return False
        if self.num_library_images >= 1:
            return False
        return True

    @property
    def number_of_observations(self):
        x = self.observations.count()
        return x

    class Meta:
        abstract = True


class WikipediaPage (models.Model):
    """
    Can be used with DSO, DSOInField,
    Planet, Comet, Asteroid, Constellation,
    MeteorShower

    Will use the a generated lookup name if
        override_lookup is not set
    Sets ambiguous/exists on lookup:
        exists = False if no page found
        ambiguous = True if disambiguation page found
    Will set summary, title, URL if found on lookup;
    """
    override_lookup = models.CharField(
        _('Override Lookup Text'),
        max_length = 100,
        null = True, blank = True,
        help_text = 'Use to handle disambiguation'
    )
    title = models.CharField(
        _('Wikipedia Title'),
        max_length = 100,
        null = True, blank = True
    )
    exists = models.PositiveIntegerField(
        _('Exists'),
        choices = YES_NO,
        null = True, blank = True,
        help_text = 'null if not looked up; false if no page exists'
    )
    ambiguous = models.PositiveIntegerField (
        _('Is Ambiguous'),
        choices = YES_NO,
        null = True, blank = True,
        help_text = 'null if not looked up; true if lookup points to a disambiguation page - need to rerun w/ override text!'
    )
    summary = models.TextField (
        _('Summary'),
        null = True, blank = True
    )
    summary_length = models.PositiveIntegerField (
        _('Summary Length'),
        null = True, blank = True
    )
    canonical_url = models.URLField (
        _('Canonical URL'),
        null = True, blank = True
    )

    @property
    def html_summary(self):
        summary = self.summary
        ss = summary.split('\n')
        html = ''
        for s in ss:
            frag = '<p>\n\t'+ s + '\n</p>\n'
            html += frag
        return html

    def __str__(self):
        return f"{self.object}: {self.object.has_wiki}"
    
    class Meta:
        abstract = True


class WikipediaPageObject(models.Model):

    @property
    def has_wiki(self):
        if not hasattr(self, 'wiki'):
            return 'NOINSTANCE'
        wiki = self.wiki
        if wiki.exists == NO or wiki.exists is None:
            return 'NOPAGEFOUND'
        if wiki.ambiguous == YES:
            return 'AMBIGUOUSPAGE'
        if wiki.summary_length == 0:
            return 'EMPTYSUMMARY'
        return 'WIKI'
    
    @property
    def has_wiki_text(self):
        if self.has_wiki == 'NOINSTANCE':
            return "No Wiki Available"
        elif self.has_wiki == 'NOPAGEFOUND':
            return "No Wiki Page"
        elif self.has_wiki == 'AMBIGUOUSPAGE':
            return "Ambiguous Wiki Entry"
        elif self.has_wiki == 'EMPTYSUMMARY':
            return "Empty Wiki Entry"
        return "Wiki Page"

    class Meta:
        abstract = True