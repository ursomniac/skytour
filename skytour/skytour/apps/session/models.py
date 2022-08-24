import datetime
import numpy as np
from django.db import models
from django.utils.translation import gettext as _
from ..observe.models import ObservingLocation
from ..astro.time import get_last, get_julian_date
from ..astro.utils import get_limiting_magnitude
from .chain import get_all_observations, get_all_objects
from .vocabs import SESSION_STAGE_CHOICES, SEEING_CHOICES

YES_NO = [(1, 'Yes'), (0, 'No')]
YES = 1
NO = 0

class ObservingSession(models.Model):
    """
    This indexes for view on PK.   I did this instead of a DateView because 
    there is a SMALL chance that you could have two separate sessions at
    different locations.   That would REALLY complicate the url pattern.

    Instead we can probably handle things in the Admin or ListView...
    """
    # This isn't unique, because there is a CHANCE that 
    # you could go to one location and then go to another location.
    ut_date = models.DateField(
        _('UT Date'),
    )
    location = models.ForeignKey (
        ObservingLocation,
        on_delete = models.CASCADE,
        # TBD, etc. locations should be updated to Active/Provisional
        # before we have a session there.
        limit_choices_to = {'status__in': ['Active', 'Provisional']}
    )
    notes = models.TextField (
        _('Notes'),
        null = True, blank = True
    )

    def get_absolute_url(self):
        return '/session/{}'.format(self.pk)

    # Get all of the Planet/OSD/etc. observations for this session
    @property
    def session_observations(self):
        return get_all_observations(self)

    @property
    def number_objects_observed(self):
        object_dict = get_all_objects(self)
        n = 0
        for k, v in object_dict.items():
            n += v.count()
        return n

    @property
    def sqm_range(self):
        conditions = self.observingcircumstances_set.all()
        try:
            sqm_min = conditions.aggregate(models.Min('sqm'))['sqm__min']
            sqm_max = conditions.aggregate(models.Max('sqm'))['sqm__max']
            if sqm_min == sqm_max:
                return f'{sqm_min:.2f}'
            else:
                return f'{sqm_min:.2f} - {sqm_max:.2f}'
        except:
            return None

    @property
    def sqm_avg(self):
        conditions = self.observingcircumstances_set.all()
        if conditions.count() < 1:
            return None
        y = []
        for c in conditions:
            if c.sqm and c.use_sqm:
                y.append(c.sqm)
        avg = np.average(y)
        rms = np.std(y)
        s = f"{avg:.2f}"
        if rms > 0:
            s += f' ± {rms:.2f}'
        return s

    @property
    def seeing_range(self):
        try:
            conditions = self.observingcircumstances_set.all()
            see_min = conditions.aggregate(models.Min('seeing'))['seeing__min']
            see_max = conditions.aggregate(models.Max('seeing'))['seeing__max']
            if see_min == see_max:
                return f'{see_min}'
            else:
                return f'{see_min} to {see_max}'
        except:
            return None

    def __str__(self):
        return f"{self.ut_date}: {self.location}"

    class Meta:
        # This mitigates the ">1 places on the same night issue"
        ordering = ['-ut_date', '-pk'] 
        unique_together = ['ut_date', 'location']


class ObservingCircumstances(models.Model):
    # Each of these have a start and an end...
    session = models.ForeignKey(
        ObservingSession,
        on_delete = models.CASCADE
    )
    ut_datetime = models.DateTimeField (
        _('UTDT'),
        default=datetime.datetime.utcnow
    )
    session_stage = models.CharField(
        _('Session Stage'),
        max_length = 20,
        choices = SESSION_STAGE_CHOICES,
        null = True, blank = True,
        default = 'during'
    )
    seeing = models.PositiveIntegerField (
        _('Seeing'),
        choices = SEEING_CHOICES,
        null = True, blank = True,
        help_text = "1 (poor) to 5 (excellent)"
    )
    sqm = models.FloatField (
        _('SQM'),
        null = True, blank = True
    )
    use_sqm = models.PositiveIntegerField (
        _('Use SQM in Stats'),
        choices = YES_NO,
        default = YES
    )
    temperature = models.IntegerField (
        _('Temperature'),
        null = True, blank = True,
        help_text = '°F'
    )
    humidity = models.PositiveIntegerField (
        _('Humidity'),
        null = True, blank = True,
        help_text = 'in %'
    )
    cloud_cover = models.PositiveIntegerField (
        _('Cloud Cover'),
        null = True, blank=True,
        help_text = 'in %'
    )
    wind = models.CharField (
        _('Wind'),
        max_length = 50,
        null = True, blank = True,
        help_text = 'Speed/Direction'
    )
    notes = models.TextField (
        _('Notes'),
        null = True, blank = True
    )
    moon = models.BooleanField (
        _('Moon'),
        default = False
    )

    url_path = None
    object_type = 'Condition'

    @property
    def brightness(self):
        x = 8.033 - 0.4 * self.sqm
        return 10**x

    @property
    def bortle(self):
        sqm_ranges = [
            (22.00, 23.00), # 1
            (21.90, 21.99), # 2
            (21.70, 21.89), # 3
            (20.50, 21.69), # 4
            (19.50, 20.49), # 5
            (18.95, 19.49), # 6
            (18.38, 18.94), # 7
            (17.80, 18.38), # 8
            (00.00, 17.79), # 9
        ]
        sqm = int(100.*(self.sqm + 0.005))/100. # round to 2 places
        for b in range(9):
            if sqm >= b[0] and sqm <= b[1]:
                return b + 1
        return None # shouldn't get here

    @property
    def limiting_magnitude(self):
        return get_limiting_magnitude(self.bortle)

    @property
    def julian_date(self):
        return get_julian_date(self.ut_datetime)
        
    @property
    def sidereal_time(self):
        return get_last(self.ut_datetime, self.session.location.longitude)

    class Meta:
        ordering = ['-ut_datetime']
        verbose_name = 'Conditions'
        verbose_name_plural = 'Observing Conditions'

    def __str__(self):
        return "{}: {}".format(self.ut_datetime, self.session_stage, self.session.location)
