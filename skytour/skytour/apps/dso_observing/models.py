from django.db import models
from django.utils.translation import gettext as _
from django.utils.html import mark_safe

from ..dso.models import DSO
from .vocabs import OBSERVING_MODE_TYPES, \
    STATUS_CHOICES, MODE_VIABILITY_CHOICES, MODE_PRIORITY_CHOICES, \
    VIABILITY_BACKGROUND_COLORS as VBC, VIABILITY_FOREGROUND_COLORS as VFC

class TargetObservingMode(models.Model):
    target = models.ForeignKey('TargetDSO', on_delete=models.CASCADE)
    # The mode for this target?
    mode = models.CharField(
        _('Observing Mode'),
        max_length = 10,
        choices = OBSERVING_MODE_TYPES
    )
    # For this mode, how difficult will this target be?
    viable = models.PositiveSmallIntegerField(
        _('Viability'),
        choices = MODE_VIABILITY_CHOICES
    )
    # Priority: 0 = none to 4 highest
    priority = models.PositiveSmallIntegerField(
        choices=MODE_PRIORITY_CHOICES,
        null = True, blank = True # For now - this should be required post-seeding
    )
    # Is this target visually interesting?
    interesting = models.BooleanField(default=False)
    # Is this target a 'challenge' for this mode?
    challenging = models.BooleanField(default=False)
    # What are the issues for this target using this mode?
    # Let's make this easier: comma-separated codes we can split and look up
    issues = models.CharField(
        _('Challenge Codes'),
        max_length = 250,
        null = True, blank = True,
        help_text = 'Comma separated list of codes - other issues in notes or quoted'
    )
    description_flags = models.CharField(
        _('Description Flags'),
        max_length = 250,
        null = True, blank = True,
        help_text = 'Comma-separated list of codes - other issues in notes or quoted'
    )
    # Notes on observing this target with this mode
    notes = models.TextField(null=True, blank=True)

    def notes_flag(self):
        if self.notes is None or len(self.notes.strip()) == 0:
            return ''
        return '*'
    
    def __str__(self):
        x = f"{self.target.dso}: {self.mode} ({self.priority}, {self.viable})"
        if self.issues:
            x += f' [{self.issues}]'
        if self.description_flags:
            x += f' / {self.description_flags}'
        return x

class TargetDSO(models.Model):
    dso = models.OneToOneField(DSO, on_delete=models.CASCADE)
    # Editorial: include
    status = models.SmallIntegerField(choices=STATUS_CHOICES, default=1)
    # Notes on this object from an observing perspective
    # e.g., "A sparse diffuse open cluster", or
    #   "A bright galaxy with well-defined spiral arms"
    notes = models.TextField(null=True, blank=True)
    # Finding Chart?
    #   Either use the Atlas or the native finding charts (for now)
    ###
    # Editorial:
    ready_to_go = models.BooleanField(default=False)


    @property
    def mode_list(self):
        found = ''
        for my_mode in self.targetobservingmode_set.all():
            found += my_mode.mode
        return found
    
    @property
    def mode_set(self):
        out = ''
        for k in 'NBSMI':
            out += k if k in self.mode_list else ' '
        return out
    
    def viability_chart(self):
        out = '<pre>'
        for k in 'NBSMI':
            if k not in self.mode_list:
                continue
            mode = self.targetobservingmode_set.filter(mode=k).first()
            v = mode.viable
            out += f'<b>{k}</b>: &nbsp;' 
            out += '0 &nbsp;' if mode.priority is None else f'{mode.priority} &nbsp;'
            for i in range(11):
                val = 'X' if i == v else '&nbsp;'
                val = f'&nbsp;{val}&nbsp;'
                span = f"<span style='background-color: {VBC[i]}; color: {VFC[i]}'>"
                span += val + '</span>'
                out += span
            out += f"&nbsp;<span>{mode.get_viable_display()}</span>"
            out += '<br>'
        out += '</pre>'
        return mark_safe(out)
    
    def __str__(self):
        return f"{self.dso}: [{self.mode_list}]"

    def get_absolute_url(self):
        return '/targets/{}'.format(self.pk)
    
    class Meta:
        ordering = ['dso__constellation', 'dso__shown_name']