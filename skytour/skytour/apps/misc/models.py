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
    event = models.CharField(
        _('Event'),
        max_length = 100
    )
    description = models.TextField(
        _('Description'),
        null = True, blank=True
    )
    type = models.ForeignKey (
        EventType,
        null = True, blank=True,
        on_delete = models.CASCADE
    )