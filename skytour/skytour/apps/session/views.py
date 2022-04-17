import datetime, pytz
import io
import time
from django.http import HttpResponse
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.generic import View
from django.views.generic.base import TemplateView
from django.views.generic.detail import DetailView
from django.views.generic.edit import FormView
from django.views.generic.list import ListView
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

from ..astro.almanac import get_dark_time
from ..observe.models import ObservingLocation
from ..astro.time import get_julian_date
from ..site_parameter.helpers import find_site_parameter
from ..solar_system.helpers import ( 
    get_planet_positions, 
    get_comet_positions,
    get_visible_asteroid_positions
)
from ..solar_system.position import get_object_metadata
from ..utils.timer import compile_times
from .forms import ObservingParametersForm, PDFSelectForm
from .mixins import CookieMixin
from .models import ObservingSession
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
        asteroid_list, atimes = get_visible_asteroid_positions(utdt_start, utdt_end=utdt_end, location=my_location, time_zone=time_zone)
        context['asteroids'] = asteroid_list
        self.request.session['asteroids'] = asteroid_list
        times += atimes
        times.append((time.perf_counter(), f'Got Asteroids'))

        # Comets
        comet_list = get_comet_positions(utdt_start, utdt_end=utdt_end, location=my_location, time_zone=time_zone)
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
            mag_limit = d['mag_limit'],
            hour_angle_range = d['hour_angle_range'],
            session_length = d['session_length'],
            show_planets = d['show_planets'],
            color_scheme = d['color_scheme'],
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
        #tzone = pytz.timezone(context['time_zone'])
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
        pages = d['obs_forms']
        # Create a PDF file
        buffer = io.BytesIO()
        p = canvas.Canvas(buffer, pagesize=letter)
        p = run_pdf(p, context, skip=skip, pages=pages)
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
