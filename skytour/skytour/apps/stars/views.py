from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.generic.base import TemplateView
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from ..session.mixins import CookieMixin
from ..utils.timer import compile_times
from .models import BrightStar
from .plot import get_skymap

class BrightStarListView(ListView):
    model = BrightStar
    template_name = 'bright_star_list.html'

@method_decorator(cache_page(30), name='dispatch')
class SkyView(CookieMixin, TemplateView):
    template_name = 'skyview.html'

    def get_context_data(self, **kwargs):
        context = super(SkyView, self).get_context_data(**kwargs)
        reversed = context['color_scheme'] == 'dark'
        utdt_start = context['utdt_start']
        location = context['location']
        # get cookies
        planets = context['cookies']['planets']
        asteroid_list = context['cookies']['asteroids']
        comet_list = context['cookies']['comets']
        sun = context['cookies']['sun']
        moon = context['cookies']['moon']
        context['show_moon'] =  moon is not None and moon['session']['start']['is_up']

        map, interesting, last, times = get_skymap(
            utdt_start, 
            location, 
            planets = planets,
            asteroid_list = asteroid_list,
            comet_list=comet_list,
            moon = moon,
            sun = sun,
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

    