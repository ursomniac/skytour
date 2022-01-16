import datetime, pytz
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.generic.base import TemplateView
from django.views.generic.edit import FormView
from ..observe.time import get_julian_date
from ..solar_system.asteroids import get_visible_asteroids
from .cookie import deal_with_cookie, update_cookie_with_asteroids
from .forms import ObservingSessionForm
from .plan import get_plan
from .utils import get_initial_from_cookie

@method_decorator(cache_page(0), name='dispatch')
class SetSessionCookieView(FormView):
    form_class = ObservingSessionForm
    template_name = 'observing_session.html'
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

        d = form.cleaned_data
        if d['set_to_now'] == 'Yes':
            utdt_start = datetime.datetime.utcnow().replace(tzinfo=pytz.utc)
        else:
            utdt_start = datetime.datetime.combine(d['date'], d['time']).replace(tzinfo=pytz.utc)
        utdt_end = utdt_start + datetime.timedelta(hours=d['session_length'])

        visible_asteroids = None
        if d['poll_asteroids'] == 'Yes':
            visible_asteroids = get_visible_asteroids(utdt_start)
            
        # Set primary cookies
        context['cookie'] = self.request.session['user_preferences'] = dict(
            utdt_start=utdt_start.isoformat(),
            utdt_end=utdt_end.isoformat(),
            location = d['location'].pk,
            julian_date = get_julian_date(utdt_start),
            dec_limit = d['dec_limit'],
            mag_limit = d['mag_limit'],
            hour_angle_range = d['hour_angle_range'],
            session_length = d['session_length'],
            show_planets = d['show_planets'],
            visible_asteroids = None
        )
        context['completed'] = True
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
        # Update context from the plan generator
        context = get_plan(context)

        # Update the cookie with the asteroids since we know this here.
        slugs = update_cookie_with_asteroids(self.request, context.get('asteroids', None))
        context['now'] = datetime.datetime.utcnow().replace(tzinfo=pytz.utc)
        return context
