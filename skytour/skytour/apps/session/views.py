import datetime, pytz
import io
import numpy as np
import pandas as pd
import time
from django.core.exceptions import ValidationError
from django.db.models import Count
from django.http import HttpResponse
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.generic import View
from django.views.generic.base import TemplateView
from django.views.generic.detail import DetailView
from django.views.generic.edit import FormView, CreateView
from django.views.generic.list import ListView
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

from ..astro.almanac import get_dark_time
from ..astro.time import get_julian_date
from ..dso.helpers import lookup_dso
from ..dso.models import DSOObservation, DSO
from ..observe.models import ObservingLocation
from ..site_parameter.helpers import find_site_parameter
from ..solar_system.helpers import ( 
    get_planet_positions, 
    get_comet_positions,
    get_visible_asteroid_positions
)
from ..solar_system.models import (
    Asteroid, AsteroidObservation,
    Comet, CometObservation,
    Planet, PlanetObservation,
    MoonObservation
)
from ..solar_system.position import get_object_metadata
from ..tech.models import Telescope
from ..utils.timer import compile_times
from .cookie import get_all_cookies, deal_with_cookie
from .forms import (
    ObservingConditionsForm,
    ObservingParametersForm, 
    PDFSelectForm, 
    SessionAddForm
)
from .mixins import CookieMixin
from .models import ObservingSession, ObservingCircumstances
from .pdf import run_pdf
from .plan import get_plan
from .utils import get_initial_from_cookie

#@method_decorator(cache_page(0), name='dispatch')
class SetSessionCookieView(FormView):
    form_class = ObservingParametersForm
    template_name = 'observing_parameters.html'
    success_url = '/session/plan'  

    def get_initial(self):
        initial = super().get_initial() # needed since we override?
        initial = get_initial_from_cookie(self.request, initial)
        time_zone = find_site_parameter('default-time-zone-id', None, 'positive')
        if time_zone is not None:
            initial['time_zone'] = time_zone
        return initial

    def get(self, request, *args, **kwargs):
        form = self.get_form(self.get_form_class())
        context = self.get_context_data(**kwargs)
        context['form'] = form
        return self.render_to_response(context)

    def post(self, request, *args, **kwargs):
        form = self.get_form(self.get_form_class())
        if form.is_valid():
            return self.form_valid(form, **kwargs)
        return self.form_invalid(form, **kwargs)

    def form_valid(self, form, **kwargs):
        context = self.get_context_data(**kwargs)

        # Start timer
        times = [(time.perf_counter(), 'Start')]
        d = form.cleaned_data
        location_pk = d['location'].pk
        my_location = ObservingLocation.objects.get(pk=location_pk)
        if d['set_to_now'] == 'Yes':
            utdt_start = datetime.datetime.utcnow().replace(tzinfo=pytz.utc)
        else:
            utdt_start = datetime.datetime.combine(d['ut_date'], d['ut_time']).replace(tzinfo=pytz.utc)
        local_time_zone = d['time_zone'].name
        try:
            time_zone = pytz.timezone(local_time_zone)
        except:
            time_zone = None
        utdt_end = utdt_start + datetime.timedelta(hours=d['session_length'])
        local_time_start = utdt_start.astimezone(time_zone) if time_zone is not None else None
        times.append((time.perf_counter(), f'Processed Form'))

        # ADD TWILIGHT!
        # Sun
        sun = get_object_metadata(utdt_start, 'Sun', 'sun', utdt_end=utdt_end, location=my_location, time_zone=time_zone)
        context['sun'] = sun 
        self.request.session['sun'] = sun
        times.append((time.perf_counter(), f'Got Sun'))

        # Moon
        moon = get_object_metadata(utdt_start, 'Moon', 'moon', utdt_end=utdt_end, location=my_location, time_zone=time_zone)
        context['moon'] = moon 
        self.request.session['moon'] = moon
        times.append((time.perf_counter(), f'Got Moon'))

        # Planets
        planets = get_planet_positions(utdt_start, utdt_end=utdt_end, location=my_location, time_zone=time_zone)
        context['planets'] = planets
        self.request.session['planets'] = planets
        times.append((time.perf_counter(), f'Got Planets'))

        # Asteroids
        asteroid_list, atimes = get_visible_asteroid_positions(
            utdt_start, 
            utdt_end=utdt_end, 
            #location=my_location, # This slows it down by 10x
            time_zone=time_zone
        )
        context['asteroids'] = asteroid_list
        self.request.session['asteroids'] = asteroid_list
        times += atimes
        times.append((time.perf_counter(), f'Got Asteroids'))

        # Comets
        comet_list, times = get_comet_positions(
            utdt_start, 
            utdt_end=utdt_end, 
            #location=my_location,  # This slows it down by 10x
            time_zone=time_zone,
            times=times
        )
        context['comets'] = comet_list
        self.request.session['comets'] = comet_list
        times.append((time.perf_counter(), 'Got Comets'))

        # Twilight
        twi_end, twi_begin = get_dark_time(utdt_start, my_location)
        twilight = dict(
            end=twi_end.utc_datetime().isoformat(), 
            begin=twi_begin.utc_datetime().isoformat()
        )

        # Set primary cookie
        context['cookie'] = self.request.session['user_preferences'] = dict(
            utdt_start = utdt_start.isoformat(),
            utdt_end = utdt_end.isoformat(),
            local_time_start = local_time_start.astimezone(time_zone).isoformat(),
            location = location_pk,
            time_zone = local_time_zone,
            julian_date = get_julian_date(utdt_start),
            dec_limit = d['dec_limit'],
            slew_limit = d['slew_limit'],
            mag_limit = d['mag_limit'],
            hour_angle_range = d['hour_angle_range'],
            session_length = d['session_length'],
            show_planets = d['show_planets'],
            flip_planets = d['flip_planets'],
            color_scheme = d['color_scheme'],
            atlas_dso_marker = d['atlas_dso_marker'],
            show_milky_way = d['show_milky_way'],
            twilight = twilight
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
        context['now'] = datetime.datetime.utcnow().replace(tzinfo=pytz.utc)
        return context

@method_decorator(cache_page(0), name='dispatch')
class ObservingPlanView(CookieMixin, FormView):
    template_name = 'observing_plan.html'
    form_class = PDFSelectForm

    def get_context_data(self, **kwargs):
        context = super(ObservingPlanView, self).get_context_data(**kwargs)
        context = get_plan(context)
        # Get the mid-point time from the local_time_start + 0.5 * session_length
        local_time = context['local_time_start']
        ztime = datetime.datetime.fromisoformat(local_time) #.astimezone(tzone)
        ztime += datetime.timedelta(hours=context['session_length']/2.)
        context['zenith_time'] = ztime.strftime("%A %b %-d, %Y %-I:%M %p %z")
        context['now'] = datetime.datetime.utcnow().replace(tzinfo=pytz.utc)
        context['form'] = PDFSelectForm()
        return context

    def form_valid(self, form, **kwargs):
        all = ['skymap', 'zenith', 'planets', 'asteroids', 'comets', 'moon', 'dso_lists', 'dsos']
        context = self.get_context_data(**kwargs)
        d = form.cleaned_data
        opt = d['pages']
        # Which things aren't checked?
        skip = list(set(all).difference(opt))
        # Specific fields
        planet_list = d['planets']
        dso_lists = d['dso_lists']
        pages = d['obs_forms']
        # Create a PDF file
        buffer = io.BytesIO()
        p = canvas.Canvas(buffer, pagesize=letter)
        p = run_pdf(p, context, planet_list=planet_list, dso_lists=dso_lists, skip=skip, pages=pages)
        buffer.seek(0)
        if p:
            response = HttpResponse(buffer, content_type='application/pdf')
            return response
        return self.render_to_response(context)

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
        tel_pk = find_site_parameter('default-telescope-pk', None, 'positive')
        if tel_pk is not None:
            initial['telescope'] = Telescope.objects.filter(pk=tel_pk).first()
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
            print("SHOWN NAME: ", shown_name)
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

class ObservingLogView(TemplateView):
    template_name = 'observed_objects_list.html'

    def get_context_data(self, **kwargs):
        context = super(ObservingLogView, self).get_context_data(**kwargs)
        for run in [(DSO, 'dso_list'), (Planet, 'planet_list'), (Asteroid, 'asteroid_list'), (Comet, 'comet_list')]:
            context[run[1]] = run[0].objects.annotate(nobs=Count('observations')).filter(nobs__gt=0).order_by('-nobs')
        context['table_dso_observed'] = 'dsos_observed'
        return context

class ObservingCircumstancesView(ListView):
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
        return context