from django.urls import reverse
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from django.views.generic.edit import UpdateView, CreateView

from ..session.mixins import CookieMixin
from ..site_parameter.helpers import find_site_parameter
from .forms import NewObservingLocationForm
from .models import ObservingLocation
from .plot import make_location_plot, plot_sqm_history, plot_expect_vs_observed_sqm

class ObservingLocationListView(ListView):
    model = ObservingLocation
    template_name = 'observing_location_list.html'

    def get_context_data(self, **kwargs):
        context = super(ObservingLocationListView, self).get_context_data(**kwargs)
        max_distance = find_site_parameter('max-location-distance', 60., 'float')
        all_locations = ObservingLocation.objects.all()

        sections = ['Active', 'Provisional', 'Possible', 'Issues', 'TBD', 'Distant', 'Rejected']
        locations = {}
        for s in sections:
            if s == 'Distant':
                locations[s] = all_locations.filter(travel_distance__gte=max_distance).exclude(status='Active')
            elif s != 'Active':
                    locations[s] = all_locations.filter(status=s).exclude(travel_distance__gt=max_distance)
            else:
                locations[s] = all_locations.filter(status=s)
            #print (f"LEN {s}: {locations[s].count()}")
        context['locations'] = locations
        context['sections'] = sections

        plot_locations = all_locations.exclude(travel_distance__gte=max_distance)
        context['sqm_plot'] = make_location_plot(plot_locations, 'sqm')
        context['brightness_plot'] = make_location_plot(plot_locations, 'bright')
        context['bortle_plot'] = plot_expect_vs_observed_sqm(all_locations)
        context['table_id'] = 'location_table'
        return context

class ObservingLocationDetailView(CookieMixin, DetailView):
    model = ObservingLocation
    template_name = 'observing_location_detail.html'

    def get_context_data(self, **kwargs):
        context = super(ObservingLocationDetailView, self).get_context_data(**kwargs)
        location = self.get_object()
        reversed = context['color_scheme'] == 'dark'
        context['sqm_plot'] = plot_sqm_history(location, reversed=reversed)
        return context
    
class ObservingLocationAddView(CreateView):
    model = ObservingLocation
    template_name = 'form_add_new_location.html'
    form_class = NewObservingLocationForm

    def get_context_data(self, **kwargs):
        context = super(ObservingLocationAddView, self).get_context_data(**kwargs)
        context['op'] = 'Add'
        return context

class ObservingLocationUpdateView(UpdateView):
    model = ObservingLocation
    template_name = 'form_add_new_location.html'
    form_class = NewObservingLocationForm

    def get_context_data(self, **kwargs):
        context = super(ObservingLocationUpdateView, self).get_context_data(**kwargs)
        context['op'] = 'Edit'
        return context