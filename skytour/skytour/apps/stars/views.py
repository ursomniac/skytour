from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.generic.base import TemplateView
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from ..session.cookie import deal_with_cookie
#from ..site_parameter.helpers import find_site_parameter
from ..solar_system.helpers import assemble_asteroid_list
from .forms import SkyMapForm
from .models import BrightStar
from .plot import get_skymap

class BrightStarListView(ListView):
    model = BrightStar
    template_name = 'bright_star_list.html'

@method_decorator(cache_page(30), name='dispatch')
class SkyView(TemplateView):
    template_name = 'skyview.html'

    def get_context_data(self, **kwargs):
        context = super(SkyView, self).get_context_data(**kwargs)
        context = deal_with_cookie(self.request, context)

        reversed = context['color_scheme'] == 'dark'
        utdt_start = context['utdt_start']
        location = context['location']
        asteroid_slugs = context.get('visible_asteroids', None)
        asteroid_list = assemble_asteroid_list(utdt_start, slugs=asteroid_slugs)
        context['skymap'], context['interesting'], context['sidereal_time'] = get_skymap(
            utdt_start, 
            location, 
            asteroid_list = asteroid_list,
            reversed=reversed
        )
        return context

class BrightStarDetailView(DetailView):
    model = BrightStar
    template_name = 'bright_star_detail.html'

    