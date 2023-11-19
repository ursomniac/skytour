import datetime as dt, pytz
from django.views.generic.base import TemplateView
from .utils import find_objects_at_home

def parse_imaged_value(v):
    if v == 'All':
        return None
    return v == 'Yes'

def parse_utdt(s):
    utdt = None
    if s is None or len(s.strip()) == 0:
        print(f"GOT NOTHING: [{s}]")
        return None
    has_sec = len(s.split(':')) == 3
    fmt = '%Y-%m-%d %H:%M' 
    fmt += ':%S' if has_sec else ''
    try:
        utdt = dt.datetime.strptime(s, fmt).replace(tzinfo=pytz.utc)
        print("GOT: ", utdt)
        return utdt
    except:
        print("PARSE ERROR: ", s)
        return None

class HomeObjectsView(TemplateView):
    template_name = 'home_objects.html'

    def get_context_data(self, **kwargs):
        context = super(HomeObjectsView, self).get_context_data(**kwargs)

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
        
        up_dict = find_objects_at_home(
            utdt = utdt,
            offset_hours = ut_offset, 
            imaged = imaged,
            min_priority = min_priority,
            #
            location_id = 1,
            min_dec = min_dec,
            min_alt = min_alt
        )
        if utdt:
            context['utdt'] = utdt.strftime('%Y-%m-%d %H:%M:%S')
        context['ut_offset'] = ut_offset
        context['pri'] = priority
        context['dec'] = dec if dec is not None else None
        context['alt'] = alt if alt is not None else None
        context['image_option'] = image_option

        dsos = up_dict['dsos']
        context['calc_utdt'] = up_dict['utdt']
        context['local_time'] = up_dict['utdt'].astimezone(pytz.timezone('US/Eastern')).strftime("%A %b %-d, %Y %-I:%M %p %z")
        context['dso_list'] = dsos
        context['dso_count'] = dsos.count()
        context['table_id'] = 'available_table'
        return context