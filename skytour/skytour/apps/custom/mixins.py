import datetime as dt
import pytz
from .utils import parse_imaged_value, parse_utdt
    
class CustomMixin(object):

    def get_context_data(self, **kwargs):
        context = super(CustomMixin, self).get_context_data(**kwargs)

        # Deal with the form
        utdt_str = self.request.GET.get('utdt', None)
        utdt = parse_utdt(utdt_str)
        offset = self.request.GET.get('ut_offset', None)
        ut_offset = 0. if offset is None or (len(offset.strip()) == 0) else float(offset)
        priority = self.request.GET.get('min_priority', '2')
        min_priority = 0 if priority is None or (len(priority.strip()) == 0) else int(priority)
        dec = self.request.GET.get('min_dec', None)
        min_dec = -30. if (dec is None) or (len(dec.strip()) == 0) else float(dec)
        alt = self.request.GET.get('min_alt', None)
        min_alt = 30. if alt is None or (len(alt.strip()) == 0) else float(alt)
        image_option = self.request.GET.get('imaged', 'No')
        imaged = parse_imaged_value(image_option)

        if utdt:
            context['utdt'] = utdt.strftime('%Y-%m-%d %H:%M:%S')
        else:
            context['utdt'] = None
        context['ut_offset'] = ut_offset
        context['pri'] = priority
        context['dec'] = dec if dec is not None else None
        context['alt'] = alt if alt is not None else None
        context['image_option'] = image_option
        context['imaged'] = imaged
        context['min_dec'] = min_dec
        context['min_alt'] = min_alt
        context['min_priority'] = min_priority
        return context