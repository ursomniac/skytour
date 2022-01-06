import datetime
from django import forms
from ..observe.models import ObservingLocation

class ShowPlanetForm(forms.Form):
    """
    Make it easy to move from date to date on a planet page
    """
    date = forms.DateField(initial=datetime.datetime.now)
    time = forms.TimeField(initial='01:00')
    location = forms.ModelChoiceField(
        queryset = ObservingLocation.objects.exclude(status='Rejected').order_by('travel_distance')
    )

class ObservationDateForm(forms.Form):
    date = forms.DateField(initial=datetime.datetime.now)
    time = forms.TimeField(initial='01:00')

class DateRangeForm(forms.Form):
    start_date = forms.DateField(initial=datetime.datetime.now)
    end_date = forms.DateField()