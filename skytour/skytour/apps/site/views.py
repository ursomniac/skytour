import datetime, pytz
from django.views.generic.base import TemplateView
from ..misc.utils import get_upcoming_calendar
from ..session.cookie import deal_with_cookie, get_cookie
from ..site_parameter.helpers import find_site_parameter
from ..solar_system.meteors import get_meteor_showers
from ..solar_system.helpers import get_adjacent_planets

class HomePageView(TemplateView):
    """
    Basically this just shows:
        1. the relevant Calendar entries
        2. active Meteor showers
        3. adjacent Planets
    """
    template_name = 'home.html'
    
    def get_context_data(self, **kwargs):
        context = super(HomePageView, self).get_context_data(**kwargs)
        cookie = deal_with_cookie(self.request, context)
        planets = get_cookie(self.request, 'planets')
        if planets:
            context['adjacent_planets'] = get_adjacent_planets(planets, cookie['utdt_start'])
        else:
            context['adjacent_planets'] = None
        utdt = datetime.datetime.utcnow().replace(tzinfo=pytz.utc)
        context['now'] = utdt
        context['cookie'] = cookie
        context['meteor_showers'] = get_meteor_showers(utdt=utdt)
        context['upcoming_events'] = get_upcoming_calendar(utdt)
        context['min_sep'] = find_site_parameter('adjacent-planets-separation', default=10., param_type='float')

        return context
