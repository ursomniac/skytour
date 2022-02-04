import datetime
#from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.utils.translation import gettext as _
from ..observe.models import ObservingLocation
from .vocabs import SESSION_STAGE_CHOICES, SEEING_CHOICES

class ObservingSession(models.Model):
    ut_date = models.DateField(
        _('UT Date')
    )
    location = models.ForeignKey (
        ObservingLocation,
        on_delete = models.CASCADE,
        limit_choices_to = {'status__in': ['Active', 'Provisional']}
    )

    notes = models.TextField (
        _('Notes'),
        null = True, blank = True
    )


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


    class Meta:
        ordering = ['utdt']
        verbose_name = 'Conditions'
        verbose_name_plural = 'Observing Conditions'

    def __str__(self):
        return "{}: {}".format(self.utdt, self.session_stage, self.session.location)
