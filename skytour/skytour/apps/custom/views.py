import datetime as dt, pytz
from django.views.generic.base import TemplateView
from ..session.mixins import CookieMixin
from ..site_parameter.helpers import find_site_parameter
from .mixins import CustomMixin
from .utils import assemble_gear_list, find_dsos_at_location_and_time

class DSOObjectsView(CookieMixin, CustomMixin, TemplateView):
    """
    This handles the @Now and @Cookie functions - the only difference is
        using the cookie has a GET value.  Both presume the ObservingLocation
        object in the cookie is the "right" value.
    """
    template_name = 'home_objects.html'

    def get_context_data(self, **kwargs):
        context = super(DSOObjectsView, self).get_context_data(**kwargs)
        debug = self.request.GET.get('debug', False)
        no_mask = self.request.GET.get('no_mask', 'off') == 'on'
        context['no_mask'] = no_mask
        is_scheduled  = self.request.GET.get('scheduled', 'off') == 'on'
        context['scheduled'] = is_scheduled
        use_cookie = self.request.GET.get('cookie', False)
        gear = assemble_gear_list(self.request)
        
        # Deal with location - get the ObservingLocation object from the Cookie
        location = context['cookies']['user_pref']['location']

        min_dec, max_dec = location.declination_range
        if context['min_dec'] is None:
            context['min_dec'] = min_dec
        if context['max_dec'] is None:
            context['max_dec'] = max_dec
        if context['min_alt'] is None:
            context['min_alt'] = find_site_parameter('minimim-object-altitude', default=10., param_type='float')
        if context['max_alt'] is None:
            context['max_alt'] = find_site_parameter('slew-limit', default=90., param_type='float')
        context['min_dec_string'] = f"{context['min_dec']:.1f}"
        context['max_dec_string'] = f"{context['max_dec']:.1f}"

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

        up_dict = find_dsos_at_location_and_time (
            utdt = context['utdt'],                  # UTDT of now or the cookie
            offset_hours = context['ut_offset'],     # Offset the time as instructed
            imaged = context['imaged'],              # Only (don't) show objects with library images
            min_priority = context['min_priority'],  # Filter by priority - TODO V2: change this!
            location = location,                     # ObservingLocation object from the cookie
            min_alt = context['min_alt'],            # Minimum altitude
            max_alt = context['max_alt'],            # Maximum altitude
            min_dec = context['min_dec'],            # Absolute range of declination
            max_dec = context['max_dec'],            # Absolute range of declination
            mask = not no_mask,                      # Use location mask (for trees, buildings, etc.)
            gear = gear,                             # Filter by gear choices
            scheduled = is_scheduled                 # Only show objects on active DSOList objects
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
