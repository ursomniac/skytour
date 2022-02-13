from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from .models import ObservingLocation
from .plot import make_location_plot

class ObservingLocationListView(ListView):
    model = ObservingLocation
    template_name = 'observing_location_list.html'

    def get_context_data(self, **kwargs):
        context = super(ObservingLocationListView, self).get_context_data(**kwargs)
        locations = ObservingLocation.objects.filter(travel_distance__lte=60)
        context['sqm_plot'] = make_location_plot(locations, 'sqm')
        context['brightness_plot'] = make_location_plot(locations, 'bright')
        context['table_id'] = 'location_table'
        return context

class ObservingLocationDetailView(DetailView):
    model = ObservingLocation
    template_name = 'observing_location_detail.html'

    def get_context_data(self, **kwargs):
        context = super(ObservingLocationDetailView, self).get_context_data(**kwargs)
        return context
