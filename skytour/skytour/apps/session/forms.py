from datetime import datetime
from django import forms
from ..observe.models import ObservingLocation
from .vocabs import PLANET_CHOICES

YES_NO = [
    ('Yes', 'Yes'),
    ('No', 'No')
]
class ObservingSessionForm(forms.Form):
    date = forms.DateField(initial=datetime.now)
    time = forms.TimeField(initial='20:00') # Keep? or use the astro system?
    location = forms.ModelChoiceField(
        queryset = ObservingLocation.objects.exclude(status='Rejected').order_by('travel_distance')
    )
    dec_limit = forms.FloatField(initial=-20.0)
    mag_limit = forms.FloatField(initial=12.0)
    hour_angle_range = forms.FloatField(initial=3.5)
    session_length = forms.FloatField(initial=3)
    show_planets = forms.ChoiceField(choices=PLANET_CHOICES, initial='visible')
    set_to_now = forms.ChoiceField(choices=YES_NO, initial='No')
    poll_asteroids = forms.ChoiceField(choices=YES_NO, initial='No')


    
