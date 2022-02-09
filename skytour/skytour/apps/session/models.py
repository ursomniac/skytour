import datetime
#from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.utils.translation import gettext as _
from ..observe.models import ObservingLocation
from ..utils.utils import get_limiting_magnitude
from .chain import get_all_observations
from .vocabs import SESSION_STAGE_CHOICES, SEEING_CHOICES

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

    # Get all of the Planet/OSD/etc. observations for this session
    @property
    def session_observations(self):
        return get_all_observations(self.ut_date)

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
    utdt = models.DateTimeField (
        _('UTDT'),
        default=datetime.datetime.utcnow
    )
    session_stage = models.CharField(
        _('Session Stage'),
        max_length = 20,
        choices = SESSION_STAGE_CHOICES,
        null = True, blank = True
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

    class Meta:
        ordering = ['utdt']
        verbose_name = 'Conditions'
        verbose_name_plural = 'Observing Conditions'

    def __str__(self):
        return "{}: {}".format(self.utdt, self.session_stage, self.session.location)
