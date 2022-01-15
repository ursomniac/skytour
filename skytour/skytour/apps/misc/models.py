from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey

from django.db import models
from django.utils.translation import gettext as _

class StateRegion(models.Model):
    """
    This is just to get around the observing location hard-coded states.
    """
    name = models.CharField(
        _('Name'),
        max_length = 40
    )
    slug = models.SlugField(
        _('Slug'),
        help_text = 'Put the abbreviation here.'
    )
    marker = models.CharField (
        _('Marker for Plot'),
        max_length = 5,
        default = 'o'
    )

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['slug']

class TimeZone(models.Model):
    """
    This is to get around the observing location hard-coded time zone.
    """
    name = models.CharField(
        _('Name'),
        max_length = 40
    )
    utc_offset = models.IntegerField(
        _('UTC Offset'),
        help_text = '<0 for West, >0 for East of Greenwich'
    )

    def __str__(self):
        return "{} (UTC {:+d})".format(self.name, self.utc_offset)
    class Meta:
        ordering = ['utc_offset']

class EventType(models.Model):
    """
    CV of Event Types
    """
    name = models.CharField (
        _('Name'),
        max_length = 100
    )
    slug = models.SlugField (
        _('Slug'),
        unique=True
    )
    icon = models.CharField (
        _('Icon'),
        max_length = 10,
        default = 'x'
    )

    def __str__(self):
        return "{}: {}".format(self.name, self.icon)

    class Meta:
        ordering = ['slug']

class Calendar(models.Model):
    """
    Calendar app
    """
    date = models.DateField(
        _('Date'),
        help_text = 'Dates are assumed to be UT'
    )
    time = models.TimeField(
        _('Time'),
        null = True, blank=True,
        help_text = 'Times are assumed to be UT'
    )
    title = models.CharField(
        _('Event'),
        max_length = 100
    )
    description = models.TextField(
        _('Description'),
        null = True, blank=True
    )
    event_type = models.ForeignKey (
        EventType,
        null = True, blank=True,
        on_delete = models.CASCADE
    )
    involves = models.ManyToManyField (
        'CalendarEventReference',
    )

    @property
    def reference_list(self):
        return ', '.join(self.calendareventreference_set.values_list('reference', flat=True))

    def __str__(self):
        icon = '' if not self.event_type else self.event_type.icon
        my_time = '' if not self.time else self.time
        return "{} {}: {} {}".format(self.date, my_time, icon, self.title)

    class Meta:
        verbose_name = 'Calendar Entry'
        verbose_name_plural = 'Calendar Items'
        ordering = (['-date', '-time'])

REFERENCE_MODEL_CHOICES = [
    ('Planet', 'Planet'),
    ('DSO', 'DSO'),
]
class CalendarEventReference(models.Model):
    calendar_event = models.ForeignKey(Calendar, on_delete=models.CASCADE)
    reference_type = models.CharField(
        _('Reference Model'),
        choices = REFERENCE_MODEL_CHOICES,
        max_length = 40,
        null = True, blank = True
    )
    reference = models.CharField (
        _('Reference'),
        max_length = 100,
        help_text = 'e.g., Jupiter, Io, NGC 7654, Moon, Sun'
    )

class Website(models.Model):
    name = models.CharField (
        _('Name'),
        max_length = 200
    )
    url = models.URLField (
        _('URL')
    )

    class Meta:
        ordering = ['name']