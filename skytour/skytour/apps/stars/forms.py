from datetime import datetime
from django import forms
from ..observe.models import ObservingLocation

class SkyMapForm(forms.Form):
    date = forms.DateField(initial=datetime.now)
    time = forms.TimeField(initial='01:00')
    location = forms.ModelChoiceField(
        queryset = ObservingLocation.objects.exclude(status='Rejected').order_by('travel_distance')
    )

