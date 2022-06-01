from datetime import datetime
from django import forms
from ..dso.models import DSOList
from ..observe.models import ObservingLocation
from ..misc.models import TimeZone
from ..site_parameter.helpers import find_site_parameter
from ..solar_system.models import Planet, Asteroid, Comet
from ..tech.models import Telescope, Eyepiece, Filter
from ..utils.models import Catalog
from .models import ObservingSession, ObservingCircumstances
from .vocabs import PLANET_CHOICES

YES_NO = [
    ('Yes', 'Yes'),
    ('No', 'No')
]
GRAPH_COLOR_SCHEME = [
    ('dark', 'DARK: White on Black'),
    ('light', 'LIGHT: Black on White')
]
ATLAS_DSO_MARKERS = [
    ('shapes', 'Shapes'),
    ('symbols', 'Symbols')
]

class ObservingParametersForm(forms.Form):
    ut_date = forms.DateField(initial=datetime.now, label="UT Date")
    ut_time = forms.TimeField(initial='0:00', label='UT Time')
    time_zone = forms.ModelChoiceField(
        queryset = TimeZone.objects.all().order_by('utc_offset'),
        label = 'Local Time Zone'
    )
    location = forms.ModelChoiceField(
        queryset = ObservingLocation.objects.exclude(status='Rejected').order_by('travel_distance')
    )
    dec_limit = forms.FloatField(
        initial = find_site_parameter('declination-limit', default=-20.0, param_type='float'),
        label = 'Dec. Limit (to S)'
    )
    mag_limit = forms.FloatField(
        initial = find_site_parameter('dso-mag-limit', default=11.5, param_type='float'),
        label = 'DSO Mag. Limit',
    )
    hour_angle_range = forms.FloatField(
        initial=find_site_parameter('hour-angle-range', default=3.5, param_type='float'),
        label = 'Hour Angle Limit (E/W)'
    )
    session_length = forms.FloatField(
        initial=find_site_parameter('session-length', default=3.0, param_type='float'),
        label = 'Obs. Session Length (hours)'
    )
    show_planets = forms.ChoiceField(choices=PLANET_CHOICES, initial=find_site_parameter('poll-planets', default='visible', param_type='string'))
    color_scheme = forms.ChoiceField(choices=GRAPH_COLOR_SCHEME, initial='dark')
    atlas_dso_marker = forms.ChoiceField(
        choices=ATLAS_DSO_MARKERS,
        initial='shapes',
        label = 'Atlas DSOs as Symbols or Shapes')
    show_milky_way = forms.ChoiceField(choices=YES_NO, initial='Yes')
    set_to_now = forms.ChoiceField(choices=YES_NO, initial='No')

PAGE_CHOICES = [
    ('skymap', 'SkyMap'),
    ('zenith', 'Zenith Map'),
    ('planets', 'Planets'),
    ('asteroids', 'Asteroids'),
    ('comets', 'Comets'),
    ('moon', 'Moon'),
    ('dsos', 'All DSOs')
]
class PDFSelectForm(forms.Form):
    pages = forms.MultipleChoiceField(
        widget = forms.CheckboxSelectMultiple, 
        choices=PAGE_CHOICES,
        initial = [c[0] for c in PAGE_CHOICES],
        required=False
    )
    planets = forms.ModelMultipleChoiceField(
        queryset = Planet.objects.all(),
        required=False
    )
    obs_forms = forms.IntegerField(initial=2)
    dso_lists = forms.ModelMultipleChoiceField(
        widget = forms.CheckboxSelectMultiple, 
        queryset = DSOList.objects.filter(show_on_plan=True),
        required = False,
    )

OBSERVE_TYPES = [
    ('dso', 'DSO'),
    ('planet', 'Planet'), 
    ('asteroid', 'Asteroid'), 
    ('comet', 'Comet'), 
    ('moon', 'Moon'), 
    ('other', 'Other')
]

class SessionAddForm(forms.Form):
    # Fill these in from the session cookie OR override
    session = forms.ModelChoiceField (
        queryset = ObservingSession.objects.all()
    )
    ut_date = forms.DateField(required=False, label='UT Date', initial=datetime.utcnow)
    location = forms.ModelChoiceField (
        queryset = ObservingLocation.objects.all() #filter(status__in=['active', 'provisional'])
    )
    telescope = forms.ModelChoiceField (
        queryset = Telescope.objects.all()
    )
    eyepiece = forms.ModelMultipleChoiceField (
        queryset = Eyepiece.objects.all(),
        required = False
    )
    filter = forms.ModelMultipleChoiceField (
        queryset = Filter.objects.all(),
        required = False
    )
    # Required
    ut_time = forms.TimeField(
        label='UT Time',
        initial=datetime.utcnow # utc
    )
    object_type = forms.ChoiceField(
        choices = OBSERVE_TYPES, initial='DSO'
    )
    # SOLAR SYSTEM section - Selections will be overridden in get_initial()
    planet = forms.ModelChoiceField (
        queryset = Planet.objects.all(),
        required=False
    )
    asteroid = forms.ModelChoiceField (
        queryset = Asteroid.objects.all(),
        required=False
    )
    comet = forms.ModelChoiceField (
        queryset = Comet.objects.all(),
        required=False
    )
    # DSO section 
    catalog = forms.ModelChoiceField (
        queryset = Catalog.objects.all(),
        required = False,
        label = 'DSO Catalog'
    )
    id_in_catalog = forms.CharField (
        required = False,
        label = 'ID in Catalog'
    )
    # Misc Section
    other_object = forms.CharField (
        required = False,
        help_text = 'Not supported yet...'
    )
    notes = forms.CharField (
        widget = forms.Textarea,
        required = False
    )

class ObservingConditionsForm(forms.ModelForm):

    class Meta:
        model = ObservingCircumstances
        fields = [
            'session',
            'session_stage',
            'ut_datetime',
            'seeing',
            'sqm',
            'temperature',
            'humidity',
            'cloud_cover',
            'wind',
            'notes'
        ]