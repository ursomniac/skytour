import datetime, pytz
import time
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.generic.base import TemplateView
from django.views.generic.detail import DetailView
from django.views.generic.edit import FormView
from django.views.generic.list import ListView
from ..observe.almanac import get_dark_time
from ..observe.models import ObservingLocation
from ..observe.time import get_julian_date
from ..solar_system.helpers import ( 
    get_planet_positions, 
    get_comet_positions,
    get_visible_asteroid_positions
)
from ..solar_system.position import get_object_metadata
from ..utils.timer import compile_times
from .cookie import deal_with_cookie, get_cookie
from .forms import ObservingParametersForm
from .models import ObservingSession
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
            utdt_start = datetime.datetime.combine(d['date'], d['time']).replace(tzinfo=pytz.utc)
        utdt_end = utdt_start + datetime.timedelta(hours=d['session_length'])
        times.append((time.perf_counter(), f'Processed Form'))

        # ADD TWILIGHT!
        # Sun
        sun = get_object_metadata(utdt_start, 'Sun', 'sun', utdt_end=utdt_end, location=my_location)
        context['sun'] = sun 
        self.request.session['sun'] = sun
        times.append((time.perf_counter(), f'Got Sun'))

        # Moon
        moon = get_object_metadata(utdt_start, 'Moon', 'moon', utdt_end=utdt_end, location=my_location)
        context['moon'] = moon 
        self.request.session['moon'] = moon
        times.append((time.perf_counter(), f'Got Moon'))

        # Planets
        planets = get_planet_positions(utdt_start, utdt_end=utdt_end, location=my_location)
        context['planets'] = planets
        self.request.session['planets'] = planets
        times.append((time.perf_counter(), f'Got Planets'))

        # Asteroids
        asteroid_list = get_visible_asteroid_positions(utdt_start, utdt_end=utdt_end, location=my_location)
        context['asteroids'] = asteroid_list
        self.request.session['asteroids'] = asteroid_list
        times.append((time.perf_counter(), f'Got Asteroids'))

        # Comets
        comet_list = get_comet_positions(utdt_start, utdt_end=utdt_end, location=my_location)
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
            utdt_start=utdt_start.isoformat(),
            utdt_end=utdt_end.isoformat(),
            location = location_pk,
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
class ObservingPlanView(TemplateView):
    template_name = 'observing_plan.html'

    def get_context_data(self, **kwargs):
        context = super(ObservingPlanView, self).get_context_data(**kwargs)
        # Update context from the session cookie
        context = deal_with_cookie(self.request, context)
        # Get object cookies
        cookie_dict = {}
        for k in ['sun', 'moon', 'planets', 'asteroids', 'comets']:
            cookie_dict[k] = get_cookie(self.request, k)
        # Update context from the plan generator
        context = get_plan(context, cookie_dict)
        context['now'] = datetime.datetime.utcnow().replace(tzinfo=pytz.utc)
        context['everything'] = context
        return context

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