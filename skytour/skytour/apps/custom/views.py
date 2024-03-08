import datetime as dt, pytz
from django.views.generic.base import TemplateView
from ..session.mixins import CookieMixin
from .mixins import CustomMixin
from .utils import find_objects_at_home, find_objects_at_cookie, parse_utdt


class HomeObjectsView(CustomMixin, TemplateView):
    template_name = 'home_objects.html'

    def get_context_data(self, **kwargs):
        context = super(HomeObjectsView, self).get_context_data(**kwargs)
        is_house = self.request.GET.get('house', 'off') == 'on'
        up_dict = find_objects_at_home(
            utdt = context['utdt'],
            offset_hours = context['ut_offset'], 
            imaged = context['imaged'],
            min_priority = context['min_priority'],
            #
            location_id = 1,
            min_dec = context['min_dec'],
            min_alt = context['min_alt'],
            house = is_house
        )

        dsos = up_dict['dsos']
        context['calc_utdt'] = up_dict['utdt']
        context['format_utdt'] = up_dict['utdt'].strftime("%Y-%m-%d %H:%M:%S")
        context['local_time'] = up_dict['utdt'].astimezone(pytz.timezone('US/Eastern')).strftime("%A %b %-d, %Y %-I:%M %p %z")
        context['dso_list'] = dsos
        context['dso_count'] = dsos.count()
        context['table_id'] = 'available_table'
        context['location'] = up_dict['location']
        return context
    
class CookieObjectsView(CookieMixin, CustomMixin, TemplateView):
    template_name = 'home_objects.html'

    def get_context_data(self, **kwargs):
        context = super(CookieObjectsView, self).get_context_data(**kwargs)
        is_house = self.request.GET.get('house', 'off') == 'on'
        if context['utdt'] is None:
            context['utdt'] = context['cookies']['user_pref']['utdt_start']
        
        up_dict = find_objects_at_cookie(
            utdt = context['utdt'],
            offset_hours = context['ut_offset'], 
            imaged = context['imaged'],
            min_priority = context['min_priority'],
            #
            location = context['cookies']['user_pref']['location'],
            min_dec = context['min_dec'],
            min_alt = context['min_alt'],
            house = is_house
        )
        dsos = up_dict['dsos']
        context['calc_utdt'] = up_dict['utdt']
        context['format_utdt'] = up_dict['utdt'].strftime("%Y-%m-%d %H:%M:%S")
        context['local_time'] = up_dict['utdt'].astimezone(pytz.timezone('US/Eastern')).strftime("%A %b %-d, %Y %-I:%M %p %z")
        context['dso_list'] = dsos
        context['dso_count'] = dsos.count()
        context['table_id'] = 'available_table'
        context['location'] = up_dict['location']
        return context