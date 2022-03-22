from datetime import datetime
from django import forms
from ..observe.models import ObservingLocation
from ..misc.models import TimeZone
from ..site_parameter.helpers import find_site_parameter
from .vocabs import PLANET_CHOICES

YES_NO = [
    ('Yes', 'Yes'),
    ('No', 'No')
]
GRAPH_COLOR_SCHEME = [
    ('dark', 'DARK: White on Black'),
    ('light', 'LIGHT: Black on White')
]

class ObservingParametersForm(forms.Form):
    date = forms.DateField(initial=datetime.now)
    time = forms.TimeField(initial='0:00') # Keep? or use the astro system?
    time_zone = forms.ModelChoiceField(
        queryset = TimeZone.objects.all().order_by('utc_offset')
    )
    location = forms.ModelChoiceField(
        queryset = ObservingLocation.objects.exclude(status='Rejected').order_by('travel_distance')
    )
    dec_limit = forms.FloatField(initial=find_site_parameter('declination-limit', default=-20.0, param_type='float'))
    mag_limit = forms.FloatField(initial=find_site_parameter('dso-mag-limit', default=11.5, param_type='float'))
    hour_angle_range = forms.FloatField(initial=find_site_parameter('hour-angle-range', default=3.5, param_type='float'))
    session_length = forms.FloatField(initial=find_site_parameter('session-length', default=3.0, param_type='float'))
    show_planets = forms.ChoiceField(choices=PLANET_CHOICES, initial=find_site_parameter('poll-planets', default='visible', param_type='string'))
    color_scheme = forms.ChoiceField(choices=GRAPH_COLOR_SCHEME, initial='dark')
    set_to_now = forms.ChoiceField(choices=YES_NO, initial='No')

