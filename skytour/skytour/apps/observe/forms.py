from datetime import datetime
from django import forms
from .models import ObservingLocation
from .time import TIME_ZONES

YES_NO = [
    ('Yes', 'Yes'),
    ('No', 'No')
]
PLANET_CHOICES = [
    ('visible', 'Only Above the Horizon'),
    ('all', 'All Planets')
]

class ObservingPlanForm(forms.Form):
    date = forms.DateField(initial=datetime.now)
    time = forms.TimeField(initial='20:00') # Keep? or use the astro system?
    location = forms.ModelChoiceField(
        queryset = ObservingLocation.objects.exclude(status='Rejected').order_by('travel_distance')
    )
    dec_limit = forms.FloatField(initial=-20.0)
    mag_limit = forms.FloatField(initial=12.0)
    horizon_range = forms.FloatField(initial=3.5)
    session_length = forms.FloatField(initial=3)
    time_zone = forms.ChoiceField(choices=TIME_ZONES, initial='US/Eastern')
    show_planets = forms.ChoiceField(choices=PLANET_CHOICES, initial='visible')
    dst = forms.ChoiceField(choices=YES_NO, initial='No')

