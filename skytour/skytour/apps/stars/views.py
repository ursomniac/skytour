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
            priority = int(params['priority'])
            mag_limit = params['mag_limit']
            initial = {
                'date': params['date'],
                'time': params['time'],
                'location': params['location'],
                'priority': params['priority'],
                'mag_limit': params['mag_limit']
            }
        else:
            utdt = datetime.datetime.utcnow().replace(tzinfo=pytz.utc)
            location = ObservingLocation.objects.get(pk=43)
            mag_limit = 6.0
            priority = 2
            initial = dict(
                date = utdt.strftime("%Y-%m-%d"),
                time = utdt.strftime('%H:%M'),
                location = location,
                priority = 'Highest/High/Medium',
                mag_limit = 6.0
            )
        context['utdt'] = utdt
        context['location'] = location
        context['skymap'] = get_skymap(utdt, location, mag_limit=mag_limit, priority=priority)
        context['form'] = SkyMapForm(initial=initial)
        return context

class BrightStarDetailView(DetailView):
    model = BrightStar
    template_name = 'bright_star_detail.html'

    