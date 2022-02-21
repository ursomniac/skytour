from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.generic.base import TemplateView
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from ..session.cookie import deal_with_cookie, get_cookie
from ..utils.timer import compile_times
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
        # get cookies
        planets = get_cookie(self.request, 'planets')
        asteroid_list = get_cookie(self.request, 'asteroids')
        comet_list = get_cookie(self.request, 'comets')

        map, interesting, last, times = get_skymap(
            utdt_start, 
            location, 
            planets = planets,
            asteroid_list = asteroid_list,
            comet_list=comet_list,
            reversed=reversed
        )
        context['skymap'] = map
        context['interesting'] = interesting
        context['sidereal_time'] = last
        # Deal with times
        context['times'] = compile_times(times)
        return context

class BrightStarDetailView(DetailView):
    model = BrightStar
    template_name = 'bright_star_detail.html'

    