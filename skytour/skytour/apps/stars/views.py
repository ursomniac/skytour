import datetime, pytz
from dateutil.parser import parse as parse_to_datetime
from django.views.generic.base import TemplateView
from django.views.generic.detail import DetailView
from django.views.generic.edit import FormView
from django.views.generic.list import ListView
from ..observe.models import ObservingLocation
from .forms import SkyMapForm
from .models import BrightStar
from .plot import get_skymap

class BrightStarListView(ListView):
    model = BrightStar
    template_name = 'bright_star_list.html'

    def get_context_data(self, **kwargs):
        context = super(BrightStarListView, self).get_context_data(**kwargs)
        params = self.request.GET
        if 'date' in params.keys():
            xdate = params['date']
            xtime = params['time']
            utdt = parse_to_datetime(xdate+' '+xtime).replace(tzinfo=pytz.utc)
            loc_pk = params['location']
            location = ObservingLocation.objects.get(pk=loc_pk)
            initial = {
                'date': params['date'],
                'time': params['time'],
                'location': params['location']
            }
        else:
            utdt = datetime.datetime.utcnow().replace(tzinfo=pytz.utc)
            location = ObservingLocation.objects.get(pk=43)
            initial = {}
        context['utdt'] = utdt
        context['location'] = location
        context['skymap'] = get_skymap(utdt, location)
        context['form'] = SkyMapForm(initial=initial)
        return context

class BrightStarDetailView(DetailView):
    model = BrightStar
    template_name = 'bright_star_detail.html'

    