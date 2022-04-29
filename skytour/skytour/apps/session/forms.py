from datetime import datetime
from django import forms
from ..dso.models import DSO
from ..observe.models import ObservingLocation
from ..misc.models import TimeZone
from ..site_parameter.helpers import find_site_parameter
from ..solar_system.models import Planet, Asteroid, Comet
from ..tech.models import Telescope, Eyepiece, Filter
from ..utils.models import Catalog
from .models import ObservingSession
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
    set_to_now = forms.ChoiceField(choices=YES_NO, initial='No')

PAGE_CHOICES = [
    ('skymap', 'SkyMap'),
    ('zenith', 'Zenith Map'),
    ('planets', 'Planets'),
    ('asteroids', 'Asteroids'),
    ('comets', 'Comets'),
    ('moon', 'Moon'),
    ('dso_lists', 'DSO Lists'),
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
    ut_date = forms.DateField(required=False, label='UT Date')
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
    ut_time = forms.TimeField(label='UT Time')
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

    #def __init__(self, *args, **kwargs):
    #    OT = {'asteroid': 'Asteroid', 'comet': 'Comet', 'dso': 'DSO', 
    #        'planet': 'Planet', 'moon': 'Moon', 'other': 'Other'}
    #    if 'object_type' in kwargs:
    #        object_type = kwargs.pop('object_type')
    #        if object_type is not None:
    #            otot = OT[object_type]
    #            print ("OTOT: ", otot)
    #            #kwargs.update(initial={'object_type': OT[object_type]})
    #            kwargs.update(initial={'object_type': None})
    #    if 'pk' in kwargs and object_type is not None:
    #        print ("GOT HERE")
    #        pk = int(kwargs.pop('pk'))
    #        if object_type == 'planet':
    #            kwargs.update(initial={'planet': Planet.objects.filter(pk=pk).first()})
    #        elif object_type == 'asteroid':
    #            kwargs.update(initial={'asteroid': Asteroid.objects.filter(pk=pk).first()})
    #        elif object_type == 'comet':
    #            kwargs.update(initial={'comet': Comet.objects.filter(pk=pk).first()})
    #        elif object_type == 'dso':
    #            dso = DSO.objects.filter(pk=pk).first()
    #            if dso:
    #                kwargs.update(
    #                    initial={
    #                        'catalog': dso.catalog,
    #                        'id_in_catalog': dso.id_in_catalog
    #                    }
    #                )
    #    else:
    #        return
    #    print ("GOT HERE 2")
    #    super(SessionAddForm, self).__init__(*args, **kwargs)

class StartSessionForm(forms.Form):
    ut_date = forms.DateField ()
    location = forms.ModelChoiceField (
        queryset = ObservingLocation.objects.filter(status__in=['provisional', 'active'])
    )