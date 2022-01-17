import datetime, pytz
from django.db import models
from django.utils.translation import gettext as _
from ..observe.models import ObservingLocation
from .vocabs import PLANET_CHOICES

class ObservingSession(models.Model):
    utdt_start = models.DateTimeField (
        _('UTDT Start'),
        default=datetime.datetime.utcnow
    )
    location = models.ForeignKey (
        ObservingLocation,
        on_delete = models.CASCADE
    )
    dec_limit = models.FloatField (
        _('Dec Limit'),
        default = -20.0
    )
    mag_limit = models.FloatField (
        _('Mag Limit'),
        default = 12.0
    )
    hour_angle_range = models.FloatField (
        _('Hour Angle Range'),
        default = 3.5
    )
    session_length = models.FloatField (
        _('Session Length'),
        default = 3.0
    )
    show_planets = models.CharField (
        _('Show Planets'),
        max_length = 10,
        choices = PLANET_CHOICES,
        default = 'visible'
    )

    def __str__(self):
        return "{}: {}".format(self.utdt_start, self.location)
