import datetime, pytz
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.generic.base import TemplateView
from django.views.generic.edit import FormView
from .forms import ObservingSessionForm

from .plan import get_plan
from .utils import get_initial_from_cookie

@method_decorator(cache_page(0), name='dispatch')
class ObservingSessionView(FormView):
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
        context['has_plan'] = True
        d = context['plan'] = get_plan(form)
        # An idea - cache the asteroids so that we don't have to go looking for them again.
        asteroid_list = d.get('asteroids', None)
        asteroid_slugs = [x['slug'] for x in asteroid_list]
        # Set cookies
        self.request.session['user_preferences'] = dict(
            utdt_start=d['utdt_start'].isoformat(),
            utdt_end=d['utdt_end'].isoformat(),
            location = d['location'].pk,
            t = d['t'],
            dec_limit = d['dec_limit'],
            mag_limit = d['mag_limit'],
            hour_angle_range = d['hour_angle_range'],
            session_length = d['session_length'],
            show_planets = d['show_planets'],
            visible_asteroids = asteroid_slugs
        )
        return self.render_to_response(context)
            
    def form_invalid(self, form, **kwargs):
        context = self.get_context_data(**kwargs)
        context['form'] = form
        context['has_plan'] = False
        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        context = super(ObservingSessionView, self).get_context_data(**kwargs)
        context['now'] = datetime.datetime.utcnow().replace(tzinfo=pytz.utc)
        return context

class ObservingPlanView(TemplateView):
    template_name = 'observing_plan.html'

    def get_context_data(self, **kwargs):
        context = super(ObservingPlanView, self).get_context_data(**kwargs)
        return context
