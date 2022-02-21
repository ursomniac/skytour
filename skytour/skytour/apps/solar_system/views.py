import datetime, pytz
from numpy import object0
import time
from django.views.generic.base import TemplateView
from django.views.generic.detail import DetailView
from django.views.generic.edit import FormView
from django.views.generic.list import ListView
from ..session.cookie import deal_with_cookie, get_cookie
from .asteroids import get_asteroid
from .comets import get_comet
from .forms import TrackerForm
from .helpers import get_all_planets
from .models import Comet, Planet, Asteroid
from .moon import get_moon
from .planets import get_ecliptic_positions
from .plot import (
    create_planet_finder_chart, 
    create_planet_system_view,
    plot_ecliptic_positions, 
    plot_track, 
    get_planet_map
)

class PlanetListView(ListView): # Updated!
    model = Planet 
    template_name = 'planet_list.html'

    def get_context_data(self, **kwargs):
        context = super(PlanetListView, self).get_context_data(**kwargs)
        planets = Planet.objects.order_by('pk')
        cookie = get_cookie(self.request, 'planets')
        planet_list = []
        for p in planets:
            d = cookie[p.name]
            d['n_obs'] = p.number_of_observations
            d['last_observed'] = p.last_observed
            planet_list.append(d)
        context['planet_list'] = planet_list
        return context

class PlanetDetailView(DetailView):
    model = Planet
    template_name = 'planet_detail.html'

    def get_context_data(self, **kwargs):
        context = super(PlanetDetailView, self).get_context_data(**kwargs)
        obj = self.get_object()
        context = deal_with_cookie(self.request, context)
        planets_cookie = get_cookie(self.request, 'planets')
        asteroids_cookie = get_cookie(self.request, 'asteroids')

        flipped =  obj.name in ['Mars', 'Jupiter', 'Saturn', 'Uranus', 'Neptune']
        reversed = context['color_scheme'] == 'dark'

        # Replace this after testing
        utdt_start = context['utdt_start']
        utdt_end = context['utdt_end']
        location = context['location']
        pdict = context['planet'] = planets_cookie[obj.name]
        pdict['name'] = obj.name
        
        # TODO: Put this in site-parameters?
        fov = 8. if obj.name in ['Uranus', 'Neptune'] else 20.
        mag_limit = 9. if obj.name in ['Uranus', 'Neptune'] else 6.5

        context['finder_chart'], ftimes = create_planet_finder_chart (
            utdt_start,
            obj, 
            planets_cookie,
            asteroids_cookie,
            reversed=reversed,
            mag_limit=mag_limit,
            fov=fov
        )

        context['view_image'] = create_planet_system_view(
            utdt_start,
            obj, 
            planets_cookie,
            flipped=flipped,
            reversed=reversed
        )
        
        context['planet_map'] = None
        if obj.planet_map is not None: # Mars, Jupiter
            px, py, context['planet_map'] = get_planet_map(obj, pdict['physical'])
            context['xy'] = dict(px=px, py=py)

        return context

class MoonDetailView(TemplateView):
    template_name = 'planet_detail.html'

    def get_context_data(self, **kwargs):
        context = super(MoonDetailView, self).get_context_data(**kwargs)
        context = deal_with_cookie(self.request, context)
        pdict = get_cookie(self.request, 'moon')
        pdict['name'] = 'Moon'
        planets_cookie = get_cookie(self.request, 'planets')
        asteroids_cookie = get_cookie(self.request, 'asteroids')
        reversed = context['color_scheme'] == 'dark'
        context['planet'] = pdict

        context['finder_chart'], ftimes = create_planet_finder_chart (
            context['utdt_start'],
            pdict, 
            planets_cookie,
            asteroids_cookie,
            object_type = 'moon',
            moon_cookie = pdict,
            reversed = reversed,
            mag_limit = 6.5,
            fov = 15.
        )

        context['view_image'] = create_planet_system_view(
            context['utdt_start'],
            None,  # There is no Moon model instance
            pdict, # this is the moon cookie
            object_type = 'moon',
            flipped = False,
            reversed = reversed
        )
        return context

class AsteroidListView(ListView):
    model = Asteroid
    template_name = 'asteroid_list.html'

    def get_context_data(self, **kwargs):
        context = super(AsteroidListView, self).get_context_data(**kwargs)
        context = deal_with_cookie(self.request, context)
        asteroids = Asteroid.objects.order_by('number')
        cookie = get_cookie(self.request, 'asteroids')
        asteroid_list = []
        for d in cookie:
            a = asteroids.get(number=d['number'])
            d['n_obs'] = a.number_of_observations
            d['last_observed'] = a.last_observed
            asteroid_list.append(d)
        context['asteroid_list'] = asteroid_list
        return context

class AsteroidDetailView(DetailView):
    model = Asteroid
    template_name = 'asteroid_detail.html'

    def get_context_data(self, **kwargs):
        context = super(AsteroidDetailView, self).get_context_data(**kwargs)
        object = self.get_object()
        context = deal_with_cookie(self.request, context)
        cookie = get_cookie(self.request, 'asteroids')
        planets_cookie = get_cookie(self.request, 'planets')
        reversed = context['color_scheme'] == 'dark'

        utdt_start = context['utdt_start']
        mag = None
        pdict = None
        for a in cookie: # Get apparent magnitude
            if a['name'] == object.full_name:
                pdict = a
                mag = a['observe']['apparent_magnitude']
                break
        mag_limit = mag + 0.5 if mag is not None else 10.
        mag_limit = 10 if mag_limit < 10. else mag_limit
        context['asteroid'] = pdict
        fov = 10.
        
        if pdict: # This is so you COULD go to an page for something not in the cookie
            context['finder_chart'], ftimes = create_planet_finder_chart (
                utdt_start, 
                object,
                planets_cookie=planets_cookie,
                asteroids=cookie,
                object_type = 'asteroid',
                obj_cookie = pdict,
                fov=fov, 
                reversed = reversed,
                mag_limit=mag_limit, 
            )
        return context

class CometListView(ListView):
    model = Comet
    template_name = 'comet_list.html'

    def get_context_data(self, **kwargs):
        context = super(CometListView, self).get_context_data(**kwargs)
        context = deal_with_cookie(self.request, context)
        cookie = get_cookie(self.request, 'comets')
        comets = Comet.objects.filter(status=1)
        comet_list = []
        for d in cookie: # get the observation history for each comet on the list
            comet = comets.get(pk=d['pk'])
            d['n_obs'] = comet.number_of_observations
            d['last_observed'] = comet.last_observed
            comet_list.append(d)
        context['comet_list'] = comet_list
        return context

class CometDetailView(DetailView):
    model = Comet
    template_name = 'comet_detail.html'

    def get_context_data(self, **kwargs):
        context = super(CometDetailView, self).get_context_data(**kwargs)
        context = deal_with_cookie(self.request, context)
        reversed = context['color_scheme'] == 'dark'

        object = self.get_object()
        planets = get_cookie(self.request, 'planets')
        asteroids = get_cookie(self.request, 'asteroids')
        comets = get_cookie(self.request, 'comets')

        pdict = None
        mag_limit = 10.
        for c in comets:
            if c['name'] == object.name:
                pdict = c
                pdict['n_obs'] = object.number_of_observations
                pdict['last_observed'] = object.last_observed
                mag = pdict['observe']['apparent_magnitude']
                break
        if mag:
            mag_limit = mag + 0.5 if mag < mag_limit else mag_limit

        context['comet'] = pdict

        context['finder_chart'], ftimes = create_planet_finder_chart (
            context['utdt_start'],
            object,
            planets,
            asteroids,
            object_type = 'comet',
            obj_cookie = pdict,
            fov = 10.,
            reversed = reversed,
            mag_limit = mag_limit
        )
        return context

### These are still in development.
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
        start_date = c.get('utdt_start', datetime.datetime.utcnow())
        end_date = start_date + datetime.timedelta(days=10)
        initial['start_date'] = start_date
        initial['end_date'] = end_date
        return initial

    def form_valid(self, form, **kwargs):
        context = self.get_context_data(**kwargs)
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
    
        x = d['start_date']
        utdt = datetime.datetime(x.year, x.month, x.day, 0, 0).replace(tzinfo=pytz.utc)

        context['track_image'] = plot_track(
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
            dsos=False
        )
        context['form'] = form
        return self.render_to_response(context)

class TrackerResultView(TemplateView):
    template_name = 'tracker.html'

class OrreryView(TemplateView):
    template_name = 'orrery_view.html'

    def get_context_data(self, **kwargs):
        context = super(OrreryView, self).get_context_data(**kwargs)
        context = deal_with_cookie(self.request, context)        
        utdt = context['utdt']
        planets = get_ecliptic_positions(utdt)
        context['system_image'] = plot_ecliptic_positions(planets)
        context['planets'] = planets
        # Ugh this is from the Earth's perspective!  Oops!
        ### Use the distance, and ecliptic coordinates to plot the planets
        return context

