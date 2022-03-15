import datetime, pytz
from django.views.generic.base import TemplateView
from ..misc.utils import get_upcoming_calendar, create_calendar_grid
from ..session.mixins import CookieMixin
from ..site_parameter.helpers import find_site_parameter
from ..solar_system.meteors import get_meteor_showers
from ..solar_system.helpers import get_adjacent_planets

class HomePageView(CookieMixin, TemplateView):
    """
    Basically this just shows:
        1. the relevant Calendar entries
        2. active Meteor showers
        3. adjacent Planets
    """
    template_name = 'home.html'
    
    def get_context_data(self, **kwargs):
        context = super(HomePageView, self).get_context_data(**kwargs)
        utdt = context['utdt_start'] \
            if self.request.GET.get('cookie') is not None \
            else datetime.datetime.utcnow().replace(tzinfo=pytz.utc)
        planets = context['cookies']['planets']
        if planets:
            context['adjacent_planets'] = get_adjacent_planets(planets, context['utdt_start'])
        else:
            context['adjacent_planets'] = None


        context['now'] = utdt
        context['meteor_showers'] = get_meteor_showers(utdt=utdt)
        context['upcoming_events'] = get_upcoming_calendar(utdt)
        context['min_sep'] = find_site_parameter('adjacent-planets-separation', default=10., param_type='float')
        context['grid'] = create_calendar_grid(utdt-datetime.timedelta(days=2))
        return context
