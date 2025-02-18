import datetime as dt, pytz
from django.views.generic.base import TemplateView
from ..session.mixins import CookieMixin
from .mixins import CustomMixin
from .utils import assemble_gear_list, find_dsos_at_location_and_time

class DSOObjectsView(CookieMixin, CustomMixin, TemplateView):
    template_name = 'home_objects.html'

    def get_context_data(self, **kwargs):
        context = super(DSOObjectsView, self).get_context_data(**kwargs)
        debug = self.request.GET.get('debug', False)
        no_mask = self.request.GET.get('no_mask', 'off') == 'on'
        context['no_mask'] = no_mask
        is_scheduled = self.request.GET.get('scheduled', 'off') == 'on'
        context['scheduled'] = is_scheduled
        use_cookie = self.request.GET.get('cookie', False)
        gear = assemble_gear_list(self.request)
        
        # Deal with location
        location = context['cookies']['user_pref']['location']

        if use_cookie:
            if context['utdt'] is None or context['utdt'] == 'None':
                context['utdt'] = context['cookies']['user_pref']['utdt_start']
        else: 
            context['utdt'] = dt.datetime.now(dt.timezone.utc)
        orig_utdt = context['utdt']
        if type(orig_utdt) == str:
            format_utdt = orig_utdt
        else:
            format_utdt = orig_utdt.strftime("%Y-%m-%d %H:%M:%S")
        
        if debug:
            print("Got UTDT: ", orig_utdt, format_utdt)
            print("Mask: ", not no_mask)
            print("Location: ", location, type(location))
            print("Scheduled: ", is_scheduled)
            print("Use Cookie: ",  use_cookie)

        up_dict = find_dsos_at_location_and_time (
            utdt = context['utdt'],
            offset_hours = context['ut_offset'],
            imaged = context['imaged'],
            min_priority = context['min_priority'],
            location = location,
            min_alt = context['min_alt'],
            max_alt = context['max_alt'],
            mask = not no_mask,
            gear = gear,
            scheduled = is_scheduled
        )
        dsos = up_dict['dsos']
        context['calc_utdt'] = up_dict['utdt']
        context['format_utdt'] = format_utdt
        context['local_time'] = up_dict['utdt'].astimezone(pytz.timezone('US/Eastern')).strftime("%A %b %-d, %Y %-I:%M %p %z")
        context['dso_list'] = dsos
        context['dso_count'] = dsos.count()
        context['table_id'] = 'available_table'
        context['location'] = up_dict['location']
        
        # Set gear in form
        for g in 'NBSMI':
            context[f'gear{g}'] = g if gear and g in gear else None

        return context