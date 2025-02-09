import datetime
from django import forms
from ..abstract.vocabs import IMAGING_STATUS_CHOICES
from ..astro.time import utc_now
from ..dso.models import DSOList
from ..observe.models import ObservingLocation
from ..misc.models import TimeZone
from ..site_parameter.helpers import find_site_parameter
from ..solar_system.models import Planet, Asteroid, Comet
from ..tech.models import Telescope, Eyepiece, Filter
from ..utils.models import Catalog
from .models import ObservingSession, ObservingCircumstances
from .utils import get_observing_locations
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

def get_next_utc(hours_split=10):
    utc = utc_now()
    if utc.hour >= hours_split:
        return utc + datetime.timedelta(days=1)
    return utc

def get_default_start_time():
    """
    This is crude but...
    """
    #           J   F   M   A   M   J   J   A   S   O   N   D
    H = [None,  0,  0,  0,  1,  2,  3,  2,  1,  0,  0,  0,  0]
    M = [None,  0,  0, 30, 30,  0,  0, 30, 30, 30,  0,  0,  0]
    utc = utc_now()
    month = utc.month
    return utc.replace(hour=H[month], minute=M[month], second=0, microsecond=0)

class SetNewSessionCookieForm(forms.Form):
    ut_date = forms.DateField(label="UT Date", initial=get_next_utc)
    ut_time = forms.TimeField(label='UT Time', initial=get_default_start_time)
    time_zone = forms.ModelChoiceField(
        queryset = TimeZone.objects.all().order_by('utc_offset'),
        label = 'Local Time Zone'
    )
    location = forms.ModelChoiceField(
        queryset = get_observing_locations(ObservingLocation.objects.all())
    )
    flip_planets = forms.ChoiceField(choices=YES_NO, initial='Yes')
    color_scheme = forms.ChoiceField(choices=GRAPH_COLOR_SCHEME, initial='dark')
    #atlas_dso_marker = forms.ChoiceField(
    #    choices=ATLAS_DSO_MARKERS,
    #    initial='shapes',
    #    label = 'Atlas DSOs as Symbols or Shapes'
    #)

class ObservingParametersForm(forms.Form):
    ut_date = forms.DateField(initial=get_next_utc, label="UT Date")
    ut_time = forms.TimeField(initial=get_default_start_time, label='UT Time')
    # TODO V2: remove time_zone - get from location's time_zone value
    time_zone = forms.ModelChoiceField(
        queryset = TimeZone.objects.all().order_by('utc_offset'),
        label = 'Local Time Zone'
    )
    location = forms.ModelChoiceField(
        queryset = get_observing_locations(ObservingLocation.objects.all())
        #queryset = ObservingLocation.objects.exclude(status='Rejected').order_by('travel_distance')
    )
    # TODO V2: replace with "min altitude" and set based on location's latitude
    dec_limit = forms.FloatField(
        initial = find_site_parameter('declination-limit', default=-20.0, param_type='float'),
        label = 'Dec. Limit (to S)'
    )
    # TODO V2: needed? If mode = I, then yes - used?
    slew_limit = forms.FloatField(
        initial = find_site_parameter('slew-limit', default=70.0, param_type='float'),
        label = 'Alt. Slew Limit',
    )
    # TODO V2: set default based on observing mode: Yes if S or M;  No otherwise.
    flip_planets = forms.ChoiceField(choices=YES_NO, initial='Yes')
    # TODO V2: keep
    color_scheme = forms.ChoiceField(choices=GRAPH_COLOR_SCHEME, initial='dark')
    # TODO V2: used?
    atlas_dso_marker = forms.ChoiceField(
        choices=ATLAS_DSO_MARKERS,
        initial='shapes',
        label = 'Atlas DSOs as Symbols or Shapes')

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
    ut_date = forms.DateField(required=False, label='UT Date', initial=utc_now)
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
    num_images = forms.IntegerField (
        initial = 0
    )
    imaging_status = forms.ChoiceField (
        choices = IMAGING_STATUS_CHOICES,
        initial = 0
    )
    
    # Required
    ut_time = forms.TimeField(
        label='UTX Time',
        initial=utc_now
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
    # TODO V2: set default session based on most recent session value
    class Meta:
        model = ObservingCircumstances
        fields = [
            'session',
            'session_stage',
            'ut_datetime',
            'seeing',
            'sqm',
            'use_sqm',
            'temperature',
            'humidity',
            'cloud_cover',
            'wind',
            'notes',
            'moon'
        ]