import datetime, pytz
import io
import numpy as np
import pandas as pd
import time

from django.core.exceptions import ValidationError
from django.http import HttpResponse
from django.urls import reverse, reverse_lazy
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.generic.base import TemplateView
from django.views.generic.detail import DetailView
from django.views.generic.edit import FormView, CreateView, UpdateView
from django.views.generic.list import ListView
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

from ..astro.almanac import get_dark_time
from ..astro.time import get_julian_date, utc_round_up_minutes
from ..astro.utils import get_declination_range
from ..dso.helpers import lookup_dso
from ..dso.models import DSOObservation
from ..observe.models import ObservingLocation
from ..plotting.scatter import create_histogram
from ..solar_system.helpers import ( 
    get_planet_positions, 
    get_comet_positions,
    get_visible_asteroid_positions
)
from ..solar_system.models import (
    Asteroid, AsteroidObservation,
    Comet, CometObservation,
    PlanetObservation,
    MoonObservation
)
from ..solar_system.position import get_object_metadata
from ..tech.models import Telescope
from ..utils.timer import compile_times
from .cookie import get_all_cookies, deal_with_cookie
from .forms import (
    ObservingConditionsForm,
    ObservingParametersForm, 
    PlanSelectForm,
    SessionAddForm,
)
from .mixins import CookieMixin
from .models import ObservingSession, ObservingCircumstances
from .pdf import run_pdf
from .utils import (
    get_initial_from_cookie, 
    get_observing_mode_string,
    update_initial
)

class SetSessionCookieView(FormView):
    form_class = ObservingParametersForm
    template_name = 'observing_parameters.html'
    success_url = '/session/plan'  

    def get_initial(self):
        initial = super().get_initial() # needed since we override?
        initial = get_initial_from_cookie(self.request, initial)
        return initial

    def get(self, request, *args, **kwargs):
        form = self.get_form(self.get_form_class())
        context = self.get_context_data(**kwargs)
        context['form'] = form
        
        # set up the "set to now" button on the form
        now = utc_round_up_minutes()
        context['now_date'] = now.strftime("%Y-%m-%d")
        context['now_time'] = now.strftime("%H:%M")
        return self.render_to_response(context)

    def form_valid(self, form, **kwargs):
        context = self.get_context_data(**kwargs)

        # Start timer
        times = [(time.perf_counter(), 'Start')]
        d = form.cleaned_data

        # Deal with location and all that entails
        location_pk = d['location'].pk
        my_location = ObservingLocation.objects.get(pk=location_pk)
        try:
            time_zone = pytz.timezone(my_location.time_zone.pytz_name)
        except:
            time_zone = None
            print(f"Error setting time_zone to {my_location.time_zone.pytz_name}")

        min_alt= d['min_object_altitude']
        min_dec, max_dec = get_declination_range(my_location, min_altitude=min_alt)
        dec_limit = min_dec if my_location.latitude >= 0. else max_dec

        # Deal with time/date
        utdt_start = datetime.datetime.combine(d['ut_date'], d['ut_time']).replace(tzinfo=pytz.utc)
        local_time_start = utdt_start.astimezone(time_zone) if time_zone is not None else None
        times.append((time.perf_counter(), f'Processed Form'))

        # Sun
        sun = get_object_metadata(utdt_start, 'Sun', 'sun', location=my_location)
        context['sun'] = sun 
        self.request.session['sun'] = sun
        times.append((time.perf_counter(), f'Got Sun'))

        # Moon
        moon = get_object_metadata(utdt_start, 'Moon', 'moon', location=my_location)
        context['moon'] = moon 
        self.request.session['moon'] = moon
        times.append((time.perf_counter(), f'Got Moon'))

        # Planets
        planets = get_planet_positions(utdt_start, location=my_location)
        context['planets'] = planets
        self.request.session['planets'] = planets
        times.append((time.perf_counter(), f'Got Planets'))

        # Asteroids
        asteroid_list, atimes = get_visible_asteroid_positions(
            utdt_start, 
            #location=my_location, # This slows it down by 10x
        )
        context['asteroids'] = asteroid_list
        self.request.session['asteroids'] = asteroid_list
        times += atimes
        times.append((time.perf_counter(), f'Got Asteroids'))

        # Comets
        comet_list, ctimes = get_comet_positions(
            utdt_start, 
            #location=my_location,  # This slows it down by 10x
            times=times
        )
        context['comets'] = comet_list
        self.request.session['comets'] = comet_list
        times += ctimes
        times.append((time.perf_counter(), 'Got Comets'))

        # Twilight
        twi_end, twi_begin = get_dark_time(utdt_start, my_location)
        twilight = dict(
            end=twi_end.utc_datetime().isoformat(), 
            begin=twi_begin.utc_datetime().isoformat()
        )

        # Misc.
        flip_planets = 'Yes' if d['observing_mode'] in 'SM' else 'No' # Make boolean
        observing_mode = d['observing_mode']

        # Set primary cookie
        context['cookie'] = self.request.session['user_preferences'] = dict(
            utdt_start = utdt_start.isoformat(),
            local_time_start = local_time_start.astimezone(time_zone).isoformat(),
            location = location_pk,
            time_zone = my_location.time_zone.name,
            julian_date = get_julian_date(utdt_start),
            dec_limit = dec_limit, 
            dec_range = (min_dec, max_dec),
            min_alt = min_alt,
            slew_limit = d['slew_limit'],
            flip_planets = flip_planets,
            color_scheme = d['color_scheme'],
            atlas_dso_marker = d['atlas_dso_marker'],
            twilight = twilight,
            observing_mode = observing_mode,
            observing_mode_string = get_observing_mode_string(observing_mode)
        )

        context['val'] = dict(
            ut_date = utdt_start.strftime("%Y-%m-%d"),
            ut_time = utdt_start.strftime("%H:%M"),
            location = my_location,
            min_alt = f"{d['min_object_altitude']}° = {min_dec:.1f}-{max_dec:.1f}",
            slew_limit = f"{d['slew_limit']}°",
            observing_mode = observing_mode,
            color_scheme = d['color_scheme'],
            atlas_dso_marker = d['atlas_dso_marker']
        )

        context['completed'] = True
        times.append((time.perf_counter(), f'Completed'))
        context['times'] = compile_times(times)
        return self.render_to_response(context)
            
    def form_invalid(self, form, **kwargs):
        context = self.get_context_data(**kwargs)
        context['form'] = form
        context['has_plan'] = False
        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        context = super(SetSessionCookieView, self).get_context_data(**kwargs)
        context['now'] = datetime.datetime.now(datetime.timezone.utc)
        return context

@method_decorator(cache_page(0), name='dispatch')
class ObservingPlanV2View(CookieMixin, FormView):
    template_name = 'observing_plan_v2.html'
    form_class = PlanSelectForm

    def get_asteroids(self):
        alist = self.request.session.get('asteroids', None) # list of dicts
        aslugs = [x['slug'] for x in alist]
        asteroids = Asteroid.objects.filter(slug__in=aslugs)
        return asteroids

    def get_comets(self):
        clist = self.request.session.get('comets', None) # list of dicts
        cpks = [x['pk'] for x in clist]
        comets = Comet.objects.filter(pk__in=cpks)
        return comets
    
    def get_initial(self):
        initial = super().get_initial()
        initial['asteroids'] = self.get_asteroids()
        initial['comets'] = self.get_comets()
        return initial
    
    def post(self, request, *args, **kwargs):
        form = PlanSelectForm(
            request.POST, 
            asteroids=self.get_asteroids(), 
            comets=self.get_comets()
        )
        if form.is_valid(): 
            return self.form_valid(form)
        else:
            return self.form_invalid(form)
    
    def form_invalid(self, form, **kwargs):
        context = self.get_context_data(**kwargs)
        print("FORM IS INVALID")
        print("ERRORS: ", form.errors)
        context['form'] = form
        return self.render_to_response(context)
        
    def form_valid(self, form, **kwargs):
        all = ['skymap', 'zenith', 'moon', 'dso_lists']
        context = self.get_context_data(**kwargs)
        d = form.cleaned_data
        opt = d['pages']
        # Which things aren't checked?
        skip = list(set(all).difference(opt))
        # Specific fields
        planet_list = d['planets']
        asteroid_list = d['asteroids']
        comet_list = d['comets']
        dso_lists = d['dso_lists']
        pages = d['obs_forms']

        # Create a PDF file
        buffer = io.BytesIO()
        p = canvas.Canvas(buffer, pagesize=letter)
        p = run_pdf(
            p, 
            context, 
            planet_list=planet_list, 
            asteroid_list=asteroid_list,
            comet_list=comet_list,
            dso_lists=dso_lists, 
            skip=skip, 
            pages=pages
        )
        buffer.seek(0)
        if p:
            response = HttpResponse(buffer, content_type='application/pdf')
            return response
        return self.render_to_response(context)
    
    def get_context_data(self, **kwargs):
        context = super(ObservingPlanV2View, self).get_context_data(**kwargs)
        local_time = context['local_time_start']
        ztime = datetime.datetime.fromisoformat(local_time) #.astimezone(tzone)
        context['zenith_time'] = ztime.strftime("%A %b %-d, %Y %-I:%M %p %z")
        context['now'] = datetime.datetime.now(datetime.timezone.utc)
        asteroids = self.get_asteroids()
        comets = self.get_comets()

        if self.request.method == 'GET':
            context['form'] = PlanSelectForm(asteroids=asteroids, comets=comets)

        elif self.request.method == 'POST':
            form = PlanSelectForm(self.request.POST, asteroids=asteroids, comets=comets)
            context['form'] = form
        return context

class ObservingSessionListView(ListView):
    model = ObservingSession
    template_name = 'session_list.html'

    def get_context_data(self, **kwargs):
        context = super(ObservingSessionListView, self).get_context_data(**kwargs)
        context['table_id'] = 'session_table'
        return context

class ObservingSessionCreateView(CreateView):
    model = ObservingSession
    template_name = 'session_create.html'
    fields = ['ut_date', 'location', 'notes']

class ObservingSessionDetailView(DetailView):
    model = ObservingSession
    template_name = 'session_detail.html'

    def get_object(self, queryset=None):
        if queryset is None:
            queryset = ObservingSession.objects.all()
        return queryset.first()

    def get_context_data(self, **kwargs):
        context = super(ObservingSessionDetailView, self).get_context_data(**kwargs)
        return context

class ShowCookiesView(TemplateView):
    template_name = 'session_cookies.html'

    def get_context_data(self, **kwargs):
        context = super(ShowCookiesView, self).get_context_data(**kwargs)
        for cookie in [
                'user_preferences', 'sun', 'moon', 
                'planets', 'asteroids', 'comets'
            ]:
            value = self.request.session.get(cookie, None)
            context[cookie] = value
        return context

class SessionAddView(CookieMixin, FormView):
    """
    Add Observation to Observing Session
    """
    template_name = 'session_add.html'
    success_url = '/session/add_object'
    form_class = SessionAddForm

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        cookies = get_all_cookies(self.request)
        aa = cookies['asteroids']
        aslugs = [a['slug'] for a in aa]
        aslugs.append('134340-pluto')
        form.fields['asteroid'].queryset = Asteroid.objects.filter(slug__in=aslugs)
        cc = cookies['comets']
        cslugs = [c['pk'] for c in cc]
        form.fields['comet'].queryset = Comet.objects.filter(pk__in=cslugs)
        return form

    def get_initial(self):
        initial = super().get_initial() # needed since we override?
        # Apparently get_context_data comes after get_initial...
        deal = deal_with_cookie(self.request, {})
        ut_date = deal.get('utdt_start', None)
        if ut_date is not None:
            initial['ut_date'] = ut_date.date()
            session = ObservingSession.objects.filter(ut_date=ut_date).first()
            if session:
                initial['session'] = session
        location = deal.get('location', None)
        if location is not None:
            initial['location'] = location
        # Default Telescope
        initial['telescope'] = Telescope.get_default_telescope()

        # If things are sent on the query string then use them to pre-populate fields
        pk = self.request.GET.get('pk')
        object_type = self.request.GET.get('object_type')
        if object_type is not None and pk is not None:
            initial = update_initial(initial, object_type, pk)
        return initial

    def get_context_data(self, **kwargs):
        context = super(SessionAddView, self).get_context_data(**kwargs)
        return context

    def form_valid(self, form, **kwargs):
        context = self.get_context_data(**kwargs)
        d = form.cleaned_data
        object_type = d['object_type']
        object = None

        # Get UTDT Date
        if d['ut_date'] is not None:
            ut_date = d['ut_date']
        else:
            session = d['session']
            ut_date = session.ut_date

        if object_type == 'planet':
            object = d['planet']
            obs = PlanetObservation()
        elif object_type == 'moon': # TBD
            obs = MoonObservation()
        elif object_type == 'other': # TBD
            #obj_name = d['other_object']
            pass
        elif object_type == 'asteroid':
            object = d['asteroid']
            obs = AsteroidObservation()
        elif object_type == 'comet':
            object = d['comet']
            obs = CometObservation()
        elif object_type == 'dso':
            dso_id = d['id_in_catalog'].strip()
            shown_name = f"{d['catalog'].abbreviation} {d['id_in_catalog']}"
            if d['catalog'].abbreviation == 'Sh2':
                shown_name = shown_name.replace(' ', '-')
            if d['catalog'].abbreviation == 'OTHER':
                shown_name = shown_name.replace('OTHER ','')
            object = lookup_dso(shown_name)
            if object is None:
                raise ValidationError(f"Failed to look up DSO {d['catalog']} {dso_id}")
            obs = DSOObservation()
        else:
            raise ValidationError (f"Object Type {object_type} not found!")

        if object:
            obs.object = object
        if d['ut_time'] is not None:
            obs.ut_datetime = datetime.datetime.combine(ut_date, d['ut_time']).replace(tzinfo=pytz.utc)
        else:
            obs.ut_datetime = datetime.datetime.now().replace(tzinfo=pytz.timezone('UTC')) # UTC
        obs.location = d['location']
        obs.telescope = d['telescope']
        obs.notes = d['notes']
        obs.save()
        if d['eyepiece'].count() > 0:
            obs.eyepieces.add(*d['eyepiece'])
        if d['filter'].count() > 0:
            obs.filters.add(*d['filter'])
        obs.notes = d['notes']
        obs.session = d['session']
        obs.save()

        context['message'] = f"{d['ut_time']}: Observation of {obs.target_name} logged."
        return self.render_to_response(context)

class ObservingConditionsFormView(CreateView):
    model = ObservingCircumstances
    form_class = ObservingConditionsForm
    template_name = 'obs_circumstance.html'

    def get_initial(self):
        initial = super().get_initial() # needed since we override?
        # Apparently get_context_data comes after get_initial...
        deal = deal_with_cookie(self.request, {})
        ut_date = deal.get('utdt_start', None)
        if ut_date is not None:
            initial['ut_date'] = ut_date.date()
            session = ObservingSession.objects.filter(ut_date=ut_date).first()
            if session:
                initial['session'] = session
        return initial

    def get_success_url(self):
        if self.session_id:
            return reverse(
                'session-detail',
                kwargs={'pk': self.object.session.pk}
            )

    def form_valid(self, form):
        d = form.cleaned_data
        session_id = d['session'].pk
        self.session_id = session_id
        return super().form_valid(form)

class ObservingCircumstancesView(CookieMixin, ListView):
    model = ObservingCircumstances
    template_name = 'observing_conditions_list.html'

    def get_context_data(self, **kwargs):
        context = super(ObservingCircumstancesView, self).get_context_data(**kwargs)
        qs = self.get_queryset()
        df = pd.DataFrame(qs.values('ut_datetime', 'sqm', 'temperature', 'humidity', 'session__location__sqm'))
        df = df.rename(columns={'session__location__sqm': 'lsqm'})
        df['date'] = pd.DatetimeIndex(df['ut_datetime']).date
        df['time'] = pd.DatetimeIndex(df['ut_datetime']).time
        df['dsqm'] = df['lsqm'] - df['sqm']

        # Histogram of SQM - ignore NaN values
        sqm_bins = np.linspace(20.0, 22.0, num=21)
        sqm_y, sqm_x = np.histogram(df['sqm'][~np.isnan(df['sqm'])], bins=sqm_bins)
        ytotal = int(np.sum(sqm_y))
        sqm_py = sqm_y.copy()
        sqm_py = sqm_py / (ytotal + 0.)

        plot_reversed = True
        #if 'color_scheme' in context.keys():
        #    plot_reversed = context['color_scheme'] == 'dark'

        context['sqm_hist'] = create_histogram(
            sqm_x, sqm_y,
            title = 'SQM Histogram',
            xtitle = 'SQM',
            ytitle = f'# Measures ({ ytotal } total)',
            reversed = plot_reversed
        )
        context['sqm_phist'] = create_histogram(
            sqm_x, sqm_py,
            title = 'SQM Histogram',
            xtitle = 'SQM',
            ytitle = '% of Dist.',
            reversed = plot_reversed
        )
        return context

class ObservingCircumstancesEditView(UpdateView):
    model = ObservingCircumstances
    template_name = 'edit_circumstances.html'
    form_class = ObservingConditionsForm

    def get_success_url(self):
        object = self.get_object()
        return reverse_lazy('session-detail', kwargs={'pk': object.session.pk })
