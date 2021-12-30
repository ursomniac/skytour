from datetime import datetime
from django import forms
from .models import ObservingLocation

YES_NO = [
    ('Yes', 'Yes'),
    ('No', 'No')
]

TIME_ZONES = [
    ('US/Eastern', 'US/Eastern'),
    ('Universal Time', 'Universal Time'),
    ('US/Pacific', 'US/Pacific'),
    ('US/Mountain', 'US/Mountain'),
    ('US/Central', 'US/Central')
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
    dst = forms.ChoiceField(choices=YES_NO, initial='No')
