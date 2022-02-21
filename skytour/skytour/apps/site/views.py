import datetime, pytz
from django.views.generic.base import TemplateView
from ..misc.utils import get_upcoming_calendar
from ..session.cookie import deal_with_cookie
from ..solar_system.meteors import get_meteor_showers
from ..solar_system.helpers import get_adjacent_planets, get_all_planets

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
        utdt = datetime.datetime.utcnow().replace(tzinfo=pytz.utc)
        context['now'] = utdt
        context['cookie'] = cookie
        context['meteor_showers'] = get_meteor_showers(utdt=utdt)
        planets = get_all_planets(utdt)
        context['adjacent_planets'] = get_adjacent_planets(planets)
        context['upcoming_events'] = get_upcoming_calendar(utdt)
        return context
