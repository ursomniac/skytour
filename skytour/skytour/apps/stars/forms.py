from datetime import datetime
from django import forms
from ..observe.models import ObservingLocation

PRIORITY_CHOICES = [
    (4, 'All'), (3, 'Highest/High/Medium'), 
    (2, 'Highest/High'), (1, 'Highest Only')
]

class SkyMapForm(forms.Form):
    date = forms.DateField(initial=datetime.now)
    time = forms.TimeField(initial='01:00')
    location = forms.ModelChoiceField(
        queryset = ObservingLocation.objects.exclude(status='Rejected').order_by('travel_distance')
    )
    priority = forms.ChoiceField(
        choices = PRIORITY_CHOICES,
        initial = 2
    )
    mag_limit = forms.FloatField(initial=6.0)

