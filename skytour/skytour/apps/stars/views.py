import datetime, pytz
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.generic.base import TemplateView
from django.views.generic.detail import DetailView
from django.views.generic.edit import FormView
from django.views.generic.list import ListView
from ..dso.helpers import get_simple_dso_list
from ..session.cookie import deal_with_cookie
from ..session.mixins import CookieMixin
from ..utils.timer import compile_times
from .models import BrightStar
from .forms import ZenithMagForm
from .plot import get_skymap, get_zenith_map

class BrightStarListView(ListView):
    model = BrightStar
    template_name = 'bright_star_list.html'

@method_decorator(cache_page(30), name='dispatch')
class SkyView(CookieMixin, TemplateView):
    template_name = 'skyview.html'

    def get_context_data(self, **kwargs):
        context = super(SkyView, self).get_context_data(**kwargs)
        hours = float(self.request.GET.get('hours', 0))
        simple = bool(self.request.GET.get('simple', False))
        mask = bool(self.request.GET.get('mask', False))
        utdt_now = bool(self.request.GET.get('utdt_now', False))
        min_dso_alt_form = self.request.GET.get('min_dso_alt', None)

        # Handle lowest altitude DSO limit
        if min_dso_alt_form:
            min_dso_alt_form.strip()
            min_dso_alt = float(min_dso_alt_form) if len(min_dso_alt_form) != 0 else 20.
        else:
            min_dso_alt = 20.
        # Handle color scheme
        reversed = context['color_scheme'] == 'dark'
        # Handle location of innermost circle
        slew_limit = None if 'slew_limit' not in context.keys() else context['slew_limit']
        # Set date/time for view
        utdt = context['utdt_start'] if not utdt_now else datetime.datetime.now(datetime.timezone.utc)
        location = context['location']
        # get cookies
        planets = context['cookies']['planets']
        asteroid_list = context['cookies']['asteroids']
        comet_list = context['cookies']['comets']
        sun = context['cookies']['sun']
        moon = context['cookies']['moon']

        # TODO V2.x: figure out if moon is on the plot
        context['show_moon'] =  moon is not None 
        
        context['shown_datetime'] = utdt + datetime.timedelta(hours=hours)
        context['local_time'] = context['shown_datetime'].astimezone(pytz.timezone(context['time_zone']))
        context['local_time_str'] = context['local_time'].strftime('%A %b %-d, %Y %-I:%M %p %z')
        context['mask'] = mask
        context['simple'] = simple
        context['hours'] = hours
        context['utdt_now'] = utdt_now
        context['min_dso_alt'] = min_dso_alt
        title = f"Skymap: {context['local_time_str']} - {location.name_for_header}"

        if simple:
            dso_list = get_simple_dso_list()
            asteroid_list = None
            comet_list = None
            reversed = False
            # TODO: change default location!
            #title = f"Skymap: {context['local_time_str']}"
            title = ''
        else:
            dso_list = None # Get from DSO table

        map, interesting, last, times = get_skymap(
            utdt, 
            location, 
            planets = planets,
            dso_list = dso_list,
            asteroid_list = asteroid_list,
            comet_list=comet_list,
            moon = moon,
            sun = sun,
            slew_limit = slew_limit,
            reversed=reversed,
            hours=hours,
            title=title,
            simple=simple,
            mask=mask,
            min_alt = min_dso_alt
        )

        context['offset_list'] = [z * 0.5 - 5. for z in range(21)]

        context['skymap'] = map
        context['interesting'] = interesting
        context['sidereal_time'] = last
        # Deal with times
        context['times'] = compile_times(times)
        return context

class BrightStarDetailView(DetailView):
    model = BrightStar
    template_name = 'bright_star_detail.html'

class ZenithMagView(FormView):
    form_class = ZenithMagForm
    template_name = 'zenith_view.html'
    success_url = '/stars/zenith_plot'

    def get_initial(self):
        initial = super(ZenithMagView, self).get_initial()
        c = deal_with_cookie(self.request, {})
        utdt = c.get('utdt_start', None)
        if not utdt:
            #utdt = datetime.datetime.utcXnow().replace(hour=21, minute=0, tzinfo=pytz.utc)
            utdt = datetime.datetime.now(datetime.timezone.utc).replace(hour=1, minute=0 )

        initial['ut_date'] = utdt.date()
        initial['ut_time'] = utdt.time()
        return initial

    def form_valid(self, form, **kwargs):
        context = self.get_context_data(**kwargs)
        context = deal_with_cookie(self.request, context)
        location = context['location']

        d = form.cleaned_data
        reversed = d['color_scheme'] == 'dark'
        
        utdt = datetime.datetime.combine(d['ut_date'], d['ut_time']).replace(tzinfo=pytz.utc)
        mag_limit = context['mag_limit'] = d['mag_limit']
        zenith_distance = context['zenith_distance'] = d['zenith_limit']
        context['map'], last = get_zenith_map(
            utdt, 
            location, 
            mag_limit, 
            zenith_distance,
            reversed=reversed,
            mag_offset=1.0,
            center_ra = d['center_ra'],
            center_dec = d['center_dec']
        )
        context['center_ra'] = last
        context['center_dec'] = location.latitude
        context['utdt'] = utdt
        tzone = pytz.timezone(context['time_zone'])
        local_time = utdt.astimezone(tzone)
        context['local_time'] = local_time.strftime("%A %b %-d, %Y %-I:%M %p %z")
        context['form'] = form
        context['results'] = True
        return self.render_to_response(context)

class ZenithMagResult(TemplateView):
    template_name = 'zenith_view.html'