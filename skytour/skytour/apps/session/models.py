import datetime
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.utils.translation import gettext as _
from ..observe.models import ObservingLocation
from .vocabs import PLANET_CHOICES

class ObservingSession(models.Model):
    utdt_start = models.DateTimeField (
        _('UTDT Start'),
        default=datetime.datetime.utcnow
    )
    utdt_end = models.DateTimeField (
        _('UTDT End'),
        null = True, blank = True
    )
    location = models.ForeignKey (
        ObservingLocation,
        on_delete = models.CASCADE,
        limit_choices_to = {'status__in': ['Active', 'Provisional']}
    )
    seeing = models.PositiveIntegerField (
        _('Seeing'),
        validators=[
            MinValueValidator(1),
            MaxValueValidator(5)
        ],
        null = True, blank = True,
        help_text = "1 (poor) to 5 (excellent)"
    )

    class Meta:
        ordering = ['-utdt_start']

    def __str__(self):
        return "{}: {}".format(self.utdt_start, self.location)
