from django.views.generic.base import TemplateView
from django.views.generic.detail import DetailView
from django.views.generic.edit import FormView
from django.views.generic.list import ListView

from .models import ObservingLocation
from .forms import ObservingPlanForm
from .plan import get_plan
from .plot import make_location_plot

class ObservingLocationListView(ListView):
    model = ObservingLocation
    template_name = 'observing_location_list.html'

    def get_context_data(self, **kwargs):
        context = super(ObservingLocationListView, self).get_context_data(**kwargs)
        locations = ObservingLocation.objects.filter(travel_distance__lte=60)
        context['sqm_plot'] = make_location_plot(locations, 'sqm')
        context['brightness_plot'] = make_location_plot(locations, 'bright')
        context['table_id'] = 'observing_table'
        return context

class ObservingLocationDetailView(DetailView):
    model = ObservingLocation 
    template_name = 'observing_location_detail.html'

    def get_context_data(self, **kwargs):
        context = super(ObservingLocationDetailView, self).get_context_data(**kwargs)
        return context

class ObservingPlanView(FormView):
    form_class = ObservingPlanForm
    template_name = 'observing_plan.html'
    success_url = '/observing_location/plan'  

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
        context['plan'] = get_plan(form)
        return self.render_to_response(context)
            
    def form_invalid(self, form, **kwargs):
        context = self.get_context_data(**kwargs)
        context['form'] = form
        context['has_plan'] = False
        return self.render_to_response(context)
