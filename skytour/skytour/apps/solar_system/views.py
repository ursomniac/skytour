import datetime, pytz, time
from dateutil.parser import isoparse
from django.views.generic.base import TemplateView
from django.views.generic.detail import DetailView
from django.views.generic.edit import FormView
from django.views.generic.list import ListView
from ..abstract.utils import get_real_time_conditions
from ..session.cookie import deal_with_cookie
from ..session.mixins import CookieMixin
from ..utils.timer import compile_times
from .forms import TrackerForm
from .helpers import compile_nearby_planet_list
from .models import Comet, Planet, Asteroid
from .pdf import get_rise_set
from .planets import get_ecliptic_positions
from .plot import (
    create_finder_chart, 
    create_planet_system_view,
    plot_ecliptic_positions, 
    plot_track, 
    get_planet_map
)
from .utils import (
    get_constellation, 
    get_asteroid_from_cookie, 
    get_comet_from_cookie,
    get_planet_from_cookie,
    get_position_from_cookie,
    get_object_from_cookie,
    get_fov,
    get_mag_limit
)
from .vocabs import PLANET_COLORS

class PlanetListView(CookieMixin, ListView):
    model = Planet 
    template_name = 'planet_list.html'

    def get_context_data(self, **kwargs):
        context = super(PlanetListView, self).get_context_data(**kwargs)
        planets = Planet.objects.order_by('pk')
        planet_cookie = context['cookies']['planets']
        planet_list = []
        for p in planets:
            d = planet_cookie[p.name]
            d['n_obs'] = p.number_of_observations
            d['num_library_images'] = p.num_library_images
            d['last_observed'] = p.last_observed
            d['obj_rise'], d['obj_set'], d['obj_transit'] = get_rise_set(d['almanac'])
            planet_list.append(d)

        context['planet_list'] = planet_list
        moon = context['cookies']['moon']
        context['moon_rise'], context['moon_set'], context['moon_transit'] = get_rise_set(moon['almanac'])
        pdict = get_ecliptic_positions(context['utdt_start'])
        context['system_image'], context['ecl_pos'] = plot_ecliptic_positions(pdict, context['color_scheme'] == 'dark')
        return context

class PlanetDetailView(CookieMixin, DetailView):
    model = Planet
    template_name = 'planet_detail.html'

    def get_context_data(self, **kwargs):
        context = super(PlanetDetailView, self).get_context_data(**kwargs)
            # Track performance
        times = [(time.perf_counter(), 'Start')]
        obj = self.get_object()
        planets_cookie = context['cookies']['planets']
        asteroids_cookie = context['cookies']['asteroids']
        
        flipped =  obj.name in ['Mars', 'Jupiter', 'Saturn', 'Uranus', 'Neptune'] and context['flip_planets'] == 'Yes'
        reversed = context['color_scheme'] == 'dark'

        utdt_start = context['utdt_start']
        pdict = context['planet'] = planets_cookie[obj.name]
        pdict['name'] = obj.name
        
        context['close_by'], times = compile_nearby_planet_list(obj.name, planets_cookie, utdt_start, times=times)
        times.append((time.perf_counter(), 'Got nearby planets'))
        fov = 2. if obj.name in ['Uranus', 'Neptune'] else 10.
        mag_limit = 10. if obj.name in ['Uranus', 'Neptune'] else 6.

        sun = context['cookies']['sun']
        moon = context['cookies']['moon']
        context['finder_chart'], times = create_finder_chart (
            utdt_start,
            obj, 
            planets_cookie,
            asteroids_cookie,
            reversed=reversed,
            mag_limit=mag_limit,
            flipped=False,
            fov=fov,
            sun=sun,
            moon=moon,
            show_dsos=False,
            times=times
        )

        context['view_image'], times = create_planet_system_view(
            utdt_start,
            obj, 
            planets_cookie,
            flipped=flipped,
            reversed=reversed,
            times=times
        )
        
        context['planet_map'] = None
        if obj.planet_map is not None: # Mars, Jupiter
            px, py, context['planet_map'] = get_planet_map(obj, pdict['physical'])
            context['xy'] = dict(px=px, py=py)
        context['library_slideshow'] = obj.image_library.filter(use_in_carousel=1).order_by('order_in_list')
        context['instance'] = obj
        context['times'] = compile_times(times)
        return context

class MoonDetailView(CookieMixin, TemplateView):
    template_name = 'planet_detail.html'

    def get_context_data(self, **kwargs):
        context = super(MoonDetailView, self).get_context_data(**kwargs)
        pdict = context['cookies']['moon']
        pdict['name'] = 'Moon'
        planets_cookie = context['cookies']['planets']
        asteroids_cookie = context['cookies']['asteroids']
        reversed = context['color_scheme'] == 'dark'
        context['planet'] = pdict

        context['finder_chart'], ftimes = create_finder_chart (
            context['utdt_start'],
            pdict, 
            planets_cookie,
            asteroids_cookie,
            object_type = 'moon',
            obj_cookie = pdict,
            reversed = reversed,
            mag_limit = 6.5,
            fov = 15.
        )

        context['view_image'], _ = create_planet_system_view(
            context['utdt_start'],
            None,  # There is no Moon model instance
            pdict, # this is the moon cookie
            object_type = 'moon',
            flipped = False,
            reversed = reversed
        )
        return context 

class AsteroidListView(CookieMixin, ListView):
    model = Asteroid
    template_name = 'asteroid_list.html'

    def get_context_data(self, **kwargs):
        """
        TODO: Table should include rise/set based off of the cookie.
        """
        context = super(AsteroidListView, self).get_context_data(**kwargs)
        
        # TODO: allow full list of asteroids, but this might be time consuming
        all = self.request.GET.get('all', None) is not None
        asteroids = Asteroid.objects.order_by('number')
        if all:
            asteroid_list = asteroids
        else:
            asteroid_list = []
            asteroid_cookie = context['cookies']['asteroids']
            for d in asteroid_cookie:
                a = asteroids.get(number=d['number'])
                d['n_obs'] = a.number_of_observations
                d['num_library_images'] = a.num_library_images
                d['last_observed'] = a.last_observed
                asteroid_list.append(d)
        context['asteroid_list'] = asteroid_list
        context['table_id'] = 'obs_asteroid_list'
        return context

class AsteroidDetailView(CookieMixin, DetailView):
    model = Asteroid
    template_name = 'asteroid_detail.html'

    def get_context_data(self, **kwargs):
        context = super(AsteroidDetailView, self).get_context_data(**kwargs)
        # Track performance
        times = [(time.perf_counter(), 'Start')]
        object = self.get_object()
        planets_cookie = context['cookies']['planets']
        asteroid_cookie = context['cookies']['asteroids']
        reversed = context['color_scheme'] == 'dark'
        utdt_start = context['utdt_start']
        pdict = get_asteroid_from_cookie(context['cookies'], object)
        context['asteroid'] = pdict

        foo = """
        if asteroid_cookie: # This is so you COULD go to an page for something not in the cookie
            for c, sc, mm in [
                ('finder_chart', 2., 11.), 
                ('large_scale_map', 10., 9.)
            ]:
                context[c], times = create_finder_chart (
                    utdt_start, 
                    object,
                    planets_cookie=planets_cookie,
                    asteroids=asteroid_cookie,
                    object_type = 'asteroid',
                    obj_cookie = pdict,
                    fov=sc, 
                    reversed = reversed,
                    mag_limit=mm, 
                    sun = context['cookies']['sun'],
                    moon = context['cookies']['moon'],
                    show_dsos = False,
                    times=times
                )
        """
        context['in_cookie'] = True if pdict else False
        context['library_slideshow'] = object.image_library.filter(use_in_carousel=1).order_by('order_in_list')
        context['times'] = compile_times(times)
        return context

class CometListView(CookieMixin, ListView):
    model = Comet
    template_name = 'comet_list.html'

    def get_context_data(self, **kwargs):
        """
        TODO: List should include rise/set info from the cookie.
        """
        context = super(CometListView, self).get_context_data(**kwargs)
        comets = Comet.objects.filter(status=1)
        # TODO: allow for full set of comets but this might be time consumind
        all = self.request.GET.get('all', None) is not None
        if all:
            comet_list = comets
        else:
            comet_list = []
            comet_cookie = context['cookies']['comets']
            for d in comet_cookie: # get the observation history for each comet on the list
                try:
                    comet = comets.get(pk=d['pk'])
                    d['n_obs'] = comet.number_of_observations
                    d['num_library_images'] = comet.num_library_images
                    d['last_observed'] = comet.last_observed
                    comet_list.append(d)
                except:
                    continue
        context['comet_list'] = comet_list
        context['table_id'] = 'obs_comet_list'
        return context

class CometDetailView(CookieMixin, DetailView):
    model = Comet
    template_name = 'comet_detail.html'

    def get_context_data(self, **kwargs):
        context = super(CometDetailView, self).get_context_data(**kwargs)
        # Track performance
        times = [(time.perf_counter(), 'Start')]
        reversed = context['color_scheme'] == 'dark'
        object = self.get_object()
        planets = context['cookies']['planets']
        asteroids = context['cookies']['asteroids']
        comets = context['cookies']['comets']
        pdict = None
        for c in comets:
            if c['name'] == object.name:
                pdict = c
                pdict['n_obs'] = object.number_of_observations
                pdict['last_observed'] = object.last_observed
                mag = pdict['observe']['apparent_magnitude']
                pdict['mag_offset'] = object.mag_offset
                pdict['est_mag'] = mag + object.mag_offset
                break
        # TODO V2: if pdict is None then it's not in the cookie.
        # Figure out how to add things from that
        context['comet'] = pdict

        foo = """
        if pdict:
            context['finder_chart'], times = create_finder_chart (
                context['utdt_start'],
                object,
                planets,
                asteroids,
                object_type = 'comet',
                obj_cookie = pdict,
                fov = 4.,
                reversed = reversed,
                mag_limit = 11.,
                sun = context['cookies']['sun'],
                moon = context['cookies']['moon'],
                show_dsos=False,
                times=times
            )
            times.append((time.perf_counter(), 'Finished Narrow Finder Chart'))
            context['large_scale_map'], times = create_finder_chart (
                context['utdt_start'],
                object,
                planets,
                asteroids,
                object_type = 'comet',
                obj_cookie = pdict,
                fov = 10.,
                reversed = reversed,
                mag_limit = 9.,
                sun = context['cookies']['sun'],
                moon = context['cookies']['moon'],
                show_dsos=False,
                times=times
            )
            times.append((time.perf_counter(), 'Finished Wide Finder Chart'))
        """
        context['library_slideshow'] = object.image_library.filter(use_in_carousel=1).order_by('order_in_list')
        context['times'] = compile_times(times)
        return context

class TrackerView(FormView):
    """
    Combine planet, asteroid, and comet tracking into a single view.
    """
    form_class = TrackerForm
    template_name = 'tracker.html'
    success_url = '/solar_system/track'

    def get_form_kwargs(self):
        kwargs = super(TrackerView, self).get_form_kwargs()
        c = deal_with_cookie(self.request, {})
        alist = c.get('visible_asteroids', None)
        kwargs['asteroid_list'] = alist if alist is not None and len(alist) > 0 else None
        return kwargs

    def get_initial(self):
        initial = super(TrackerView, self).get_initial()
        c = deal_with_cookie(self.request, {})
        start_date = c.get('utdt_start', datetime.datetime.now(datetime.timezone.utc))
        end_date = start_date + datetime.timedelta(days=10)
        initial['start_date'] = start_date
        initial['end_date'] = end_date
        return initial

    def form_valid(self, form, **kwargs):
        context = self.get_context_data(**kwargs)
        times = [(time.perf_counter(), 'Start')]

        context = deal_with_cookie(self.request, context)
        reversed = context['color_scheme'] == 'dark'
        d = form.cleaned_data
        model_dict = {'planet': Planet, 'asteroid': Asteroid, 'comet': Comet}
        object_type, slug = d['object'].split('--')
        if object_type not in model_dict.keys():
            context['issue'] = f'Object Type: {object_type} not found.'
            return context

        if object_type != 'comet':
            object = model_dict[object_type].objects.filter(slug=slug).first()
        else:
            object = Comet.objects.get(pk=slug)

        if not object:
            context['issue'] = f'{object_type} Object {slug} not found.'
            return context

        offset_before = 0
        offset_after = (d['end_date'] - d['start_date']).days
        step_days = d['date_step'] or 1
        step_labels = d['label_step'] or 5
        mag_limit = d['mag_limit'] or 8.
        fov = d['fov']
        dsos = d['show_dsos'] == '1'
        reversed = d['reversed'] == 'wob'
        x = d['start_date']
        utdt = datetime.datetime(x.year, x.month, x.day, 0, 0).replace(tzinfo=pytz.utc)

        context['track_image'], starting_position, track_positions, times = plot_track(
            utdt,
            object_type=object_type,
            object=object, 
            offset_before = offset_before,
            offset_after = offset_after,
            step_days = step_days,
            step_label = step_labels,
            mag_limit = mag_limit,
            fov=fov,
            reversed=reversed,
            return_data = True,
            dsos=dsos,
            times=times,
        )
        context['form'] = form
        context['track_positions'] = track_positions
        
        if starting_position:
            xra, xdec, xdist = starting_position.radec()
            context['observe'] = dict(
                ra = xra.hours.item(),
                dec = xdec.degrees.item(),
                dist =  xdist.au.item(),
                utdt = utdt
            )
            context['instance'] = object
            context['constellation'] = get_constellation(xra.hours.item(), xdec.degrees.item())
        context['times'] = compile_times(times)
        return self.render_to_response(context)

class TrackerResultView(TemplateView):
    template_name = 'tracker.html'

class OrreryView(TemplateView):
    template_name = 'orrery_view.html'

    def get_context_data(self, **kwargs):
        context = super(OrreryView, self).get_context_data(**kwargs)
        context = deal_with_cookie(self.request, context)        
        utdt = context['utdt_start']
        # Get the heliocentric ecliptic positions
        pdict = get_ecliptic_positions(utdt)
        context['system_image'], context['ecl_pos'] = plot_ecliptic_positions(pdict, reversed=False)
        return context

class PlanetRealTimeView(CookieMixin, DetailView):
    model = Planet
    template_name = 'real_time_popup.html'

    def get_context_data(self, **kwargs):
        context = super(PlanetRealTimeView, self).get_context_data(**kwargs)
        object = self.get_object()
        context['object_type'] = 'Planet'
        context['object'] = object
        planet_cookie = get_planet_from_cookie(context['cookies'], object)
        if planet_cookie:
            object.ra_float, object.dec_float = get_position_from_cookie(planet_cookie)
        context = get_real_time_conditions(object, self.request, context)
        return context
    
class AsteroidRealTimeView(CookieMixin, DetailView):
    model = Asteroid
    template_name = 'real_time_popup.html'

    def get_context_data(self, **kwargs):
        context = super(AsteroidRealTimeView, self).get_context_data(**kwargs)
        object = self.get_object()
        context['object_type'] = 'Asteroid'
        context['object'] = object
        asteroid_cookie = get_asteroid_from_cookie(context['cookies'], object)
        # get ra and dec
        if asteroid_cookie:
            object.ra_float, object.dec_float = get_position_from_cookie(asteroid_cookie)
        context = get_real_time_conditions(object, self.request, context)
        return context
    
class CometRealTimeView(CookieMixin, DetailView):
    model = Comet
    template_name = 'real_time_popup.html'

    def get_context_data(self, **kwargs):
        context = super(CometRealTimeView, self).get_context_data(**kwargs)
        object = self.get_object()
        context['object_type'] = 'Comet'
        context['object'] = object
        comet_cookie = get_comet_from_cookie(context['cookies'], object)
        if comet_cookie:
            object.ra_float, object.dec_float = get_position_from_cookie(comet_cookie)
        context = get_real_time_conditions(object, self.request, context)
        return context
    
class SSOMapView(CookieMixin, TemplateView):
    template_name = 'sso_map_popup.html'

    def get_cookie_entry(object_type, object, cookie):
        if object_type == 'planet':
            return get_planet_from_cookie

    def get_context_data(self, **kwargs):
        context = super(SSOMapView, self).get_context_data(**kwargs)
        model = {'planet': Planet, 'asteroid': Asteroid, 'comet': Comet}
        object_type = self.kwargs['object_type']
        pk = self.kwargs['pk']
        style = self.kwargs['style'] # wide | narrow
        reversed = context['color_scheme'] == 'dark'

        object = model[object_type].objects.filter(pk=pk).first()
        pdict = get_object_from_cookie(object_type, context['cookies'], object)
        planets = context['cookies']['planets']
        asteroids = context['cookies']['asteroids']
        times = [(time.perf_counter(), 'Start Creating Map')]
        fov = get_fov(object_type, object, style)
        mag_limit = get_mag_limit(object_type, object, style)

        context['map'], times = create_finder_chart (
            context['utdt_start'],
            object,
            planets,
            asteroids,
            object_type = object_type,
            obj_cookie = pdict,
            fov = fov,
            reversed = reversed,
            mag_limit = mag_limit,
            sun = context['cookies']['sun'],
            moon = context['cookies']['moon'],
            show_dsos=False,
            times=times
        )
        context['title'] = f"{style.title()} for {object.name}"
        context['fov'] = fov
        context['mag_limit'] = mag_limit
        context['times'] = compile_times(times)
        return context