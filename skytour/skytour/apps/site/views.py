import datetime, pytz
from django.views.generic.base import TemplateView
from ..solar_system.meteors import get_meteor_showers
from ..solar_system.planets import get_adjacent_planets, get_all_planets

class HomePageView(TemplateView):
    """
    TODO: come up with a reason to have a home page... :-)
    """
    template_name = 'home.html'
    
    def get_context_data(self, **kwargs):
        context = super(HomePageView, self).get_context_data(**kwargs)
        utdt = datetime.datetime.utcnow().replace(tzinfo=pytz.utc)
        context['utdt'] = utdt
        context['meteor_showers'] = get_meteor_showers(utdt=utdt)
        planets = get_all_planets(utdt)
        context['adjacent_planets'] = get_adjacent_planets(planets)
        return context
