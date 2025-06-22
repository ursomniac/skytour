from django.db import models
from django.utils.translation import gettext as _
from .utils_pytz import possible_timezones
from .vocabs import REFERENCE_MODEL_CHOICES

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
    abbreviation = models.CharField (
        _('Abbreviation'),
        max_length = 2,
        null = True, blank = True
    )

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['pk']

class Country(models.Model):
    name = models.CharField (
        _('Name '),
        max_length = 100
    )
    code = models.CharField (
        _('Code'),
        max_length = 2
    )

    def __str__(self):
        return f"{self.name} ({self.code})"
    
    class Meta:
        ordering = ['name']

class TimeZone(models.Model):
    """
    This is to get around the observing location hard-coded time zone.
    """
    ### SEED V2: Need to seed this!
    name = models.CharField(
        _('Name'),
        max_length = 40
    )
    utc_offset = models.IntegerField(
        _('UTC Offset'),
        help_text = '<0 for West, >0 for East of Greenwich'
    )
    abbreviation = models.CharField (
        _('Abbreviation'),
        max_length = 5
    )
    pytz_label = models.CharField (
        _('PYTZ Label'),
        max_length = 50,
        blank=True, null=True,
        help_text = 'Needed for local time, help with DST'
    )

    @property
    def time_code(self):
        o = self.utc_offset
        s = '+' if o >= 0.0 else '-'
        h = int(abs(o))
        m = (60 * o) % 60
        return f"{s}{h:02s}:{m:02d}"
    
    @property 
    def pytz_name(self):
        #return possible_timezones(self.utc_offset)[0]
        return self.pytz_label

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
    #involves = models.ManyToManyField (
    #    'CalendarEventReference',
    #)

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

    def __str__(self):
        return f"{self.reference_type} {self.reference}"

class Website(models.Model):
    name = models.CharField (
        _('Name'),
        max_length = 200
    )
    url = models.URLField (
        _('URL')
    )

    def __str__(self):
        return self.name
        
    class Meta:
        ordering = ['name']

class Glossary(models.Model):
    name = models.CharField (
        _('Name/Topic'),
        max_length = 100,
    )
    slug = models.SlugField (
        _('Slug'),
        unique = True
    )
    description = models.TextField (
        _('Description'),
        null = True, blank = True
    )
    link = models.URLField (
        _('Link'),
        null = True, blank = True,
        help_text = 'External link for more information'
    )
    
    def __str__(self):
        return self.name

    class Meta:
        ordering = ['slug']
        verbose_name = 'Glossary Entry'
        verbose_name_plural = 'Glossary Entries'

class PDFManual(models.Model):
    title = models.CharField(
        _('Title'),
        max_length = 100
    )
    slug = models.SlugField()
    pdf_file = models.FileField (
        _('PDF File'),
        upload_to = 'pdf_files'
    )

    def __str__(self):
        return f"{self.title} ({self.pdf_file})"
    class Meta:
        ordering = ['slug']