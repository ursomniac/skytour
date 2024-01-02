import datetime as dt
from django.db import models
from django.utils.html import mark_safe
from django.utils.translation import gettext as _
from ..abstract.models import Coordinates

class OccultingAsteroid(models.Model):
    name = models.CharField (
        _('Name'),
        max_length = 20,
        null = True, blank = True
    )
    designation = models.CharField (
        _('Designation'), 
        max_length = 20,
        help_text = 'e.g., 2000 CB82',
        null = True, blank = True
    )
    slug = models.SlugField ( 
        _('Slug'),
        help_text = 'num--name or num--designation or designation'
    )
    number = models.PositiveIntegerField (
        _('Number'),
        null = True, blank = True
    )
    h = models.FloatField (
        _('H'),
        help_text = 'absolute magnitude'
    )
    g = models.FloatField (
        _('G'),
        default = 0.15,
        help_text = 'slope parameter'
    )

    @property
    def shown_name(self):
        f = []
        if self.number is not None:
            f.append(f"({self.number})")
        if self.name is not None:
            f.append(self.name)
        else:
            f.append(self.designation)
        if len(f) == 0:
            return self.slug
        return ' '.join(f)
    
    def __str__(self):
        f = []
        if self.number is not None:
            f.append(f"{self.number}")
        if self.name is not None:
            f.append(self.name)
        else:
            y = self.designation.replace(' ','-')
            f.append(y)
        if len(f) == 0:
            return self.slug
        return '--'.join(f)
        

class OccultedStar(Coordinates):
    name = models.CharField (
        _('Name'),
        max_length = 20
    )
    magnitude = models.FloatField (
        _('Magnitude'),
        null = True, blank = True
    )
    color_index = models.FloatField (
        _('B-V Color'),
        null = True, blank = True
    )
    parallax = models.FloatField (
        _('Parallax'),
        null = True, blank = True,
        help_text = 'mas'
    )
    alias_list = models.CharField (
        _('Alias List'),
        max_length = 200,
        null = True, blank = True,
        help_text = 'separated by commas'
    )
    
    def save(self, *args, **kwargs):
        self.ra = self.ra_float # get from property
        self.dec = self.dec_float # get from property
        self.ra_text = self.format_ra # get from property
        self.dec_text = self.format_dec # get from property
        #self.shown_name = create_shown_name(self)
        super(OccultedStar, self).save(*args, **kwargs)

    def __str__(self):
        x = f"{self.pk}: {self.name}"
        if self.alias_list is not None:
            x += f" ({self.alias_list})"
        return x

class AsteroidOccultation(models.Model):
    """
    For asteroid occultations
    """
    observation_date = models.DateField (
        _('Obs. Date')
    )
    start_ut = models.TimeField (
        _('UT Start')
    )
    duration = models.FloatField (
        _('Obs. Duration'),
        help_text = 'minutes'
    )
    star = models.ForeignKey(
        OccultedStar,
        null = True,
        on_delete = models.CASCADE
    )
    asteroid = models.ForeignKey(
        OccultingAsteroid,
        null = True,
        on_delete = models.CASCADE
    )
    notes = models.TextField(
        _('Notes'),
        null = True, blank = True
    )
    path_image = models.ImageField (
        _('Path Image'),
        null = True, blank = True,
        upload_to = 'occ_paths'
    )
    # What about results - TBD

    def obs_utdt(self):
        utdt = dt.datetime.combine(self.observation_date, self.start_ut)
        return utdt
    
    @property
    def formatted_utdt(self):
        utdt = dt.datetime.combine(self.observation_date, self.start_ut)
        return utdt.strftime("%Y-%m-%d %H:%M:%S")
    
    def __str__(self):
        return f"{self.formatted_utdt}: {self.star.name} by {self.asteroid.shown_name}"