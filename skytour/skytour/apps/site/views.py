import datetime, pytz
from django.views.generic.base import TemplateView
from ..astro.calendar import get_upcoming_calendar, create_calendar_grid
from ..session.mixins import CookieMixin
from ..site_parameter.helpers import find_site_parameter
from ..solar_system.meteors import get_meteor_showers
from ..solar_system.helpers import get_adjacent_planets
from .utils import (
    observation_table, 
    get_last_observing_session,
    get_most_popular_observing_locations,
    number_of_days_since_last_observing_session,
    get_random_dso_library_image,
    get_skytour_version
)

class HomePageView(TemplateView):
    template_name = 'home.html'

    def get_context_data(self, **kwargs):
        context = super(HomePageView, self).get_context_data(**kwargs)
        context['version'] = get_skytour_version()
        context['observation_table'] = observation_table() 
        context['most_recent_session'] = get_last_observing_session()
        context['days_since_last_session'] = number_of_days_since_last_observing_session()
        context['top_5_locations'] = get_most_popular_observing_locations(n=5)
        context['random_dso_image'] = get_random_dso_library_image()
        return context

class TodayPageView(CookieMixin, TemplateView):
    """
    Basically this just shows:
        1. the relevant Calendar entries
        2. active Meteor showers
        3. adjacent Planets
    """
    template_name = 'today.html'
    
    def get_context_data(self, **kwargs):
        context = super(TodayPageView, self).get_context_data(**kwargs)
        utdt = context['utdt_start'] \
            if self.request.GET.get('cookie') is not None \
            else datetime.datetime.now(datetime.timezone.utc)
        context['utdt'] = utdt
        planets = context['cookies']['planets']
        if planets:
            context['adjacent_planets'], _ = get_adjacent_planets(planets, context['utdt_start'])
        else:
            context['adjacent_planets'] = None
        if 'time_zone' in context.keys():
            time_zone = pytz.timezone(context['time_zone'])
        else:
            time_zone = None
        
        context['now'] = utdt
        context['meteor_showers'] = get_meteor_showers(utdt=utdt)
        context['upcoming_events'] = get_upcoming_calendar(utdt)
        context['min_sep'] = find_site_parameter('adjacent-planets-separation', default=10., param_type='float')
        context['grid'] = create_calendar_grid(utdt-datetime.timedelta(days=2), time_zone=time_zone)
        return context
