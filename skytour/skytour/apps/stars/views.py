import datetime, pytz
from dateutil.parser import parse as parse_to_datetime
from django.views.generic.base import TemplateView
from django.views.generic.detail import DetailView
from django.views.generic.edit import FormView
from django.views.generic.list import ListView
from ..observe.models import ObservingLocation
from ..session.cookie import deal_with_cookie
from .forms import SkyMapForm
from .models import BrightStar
from .plot import get_skymap

class BrightStarListView(ListView):
    model = BrightStar
    template_name = 'bright_star_list.html'

class SkyView(TemplateView):
    template_name = 'skyview.html'

    def get_context_data(self, **kwargs):
        context = super(SkyView, self).get_context_data(**kwargs)
        context = deal_with_cookie(self.request, context)
        print ("CONTEXT: ", context)
        utdt_start = context['utdt_start']
        location = context['location']
        priority = 2 # Set this in Admin
        mag_limit = 6. # Set this in Admin
        asteroid_list = context.get('visible_asteroids', None)
        print ("ASTEROID LIST: ", asteroid_list)
        context['skymap'] = get_skymap(
            utdt_start, 
            location, 
            mag_limit=mag_limit, 
            priority=priority,
            asteroid_list = asteroid_list
        )
        return context

class BrightStarDetailView(DetailView):
    model = BrightStar
    template_name = 'bright_star_detail.html'

    