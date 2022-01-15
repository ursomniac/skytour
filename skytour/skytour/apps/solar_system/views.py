import datetime, pytz
from dateutil.parser import parse as parse_to_datetime
from django.views.generic.base import TemplateView
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from ..session.cookie import deal_with_cookie

from .asteroids import get_asteroid, get_all_asteroids
from .models import Planet, Asteroid, MeteorShower
from .moon import get_moon
from .planets import get_all_planets, get_ecliptic_positions
from .plot import create_planet_image, plot_ecliptic_positions, plot_track, get_planet_map

class PlanetListView(ListView):
    model = Planet 
    template_name = 'planet_list.html'

    def get_context_data(self, **kwargs):
        context = super(PlanetListView, self).get_context_data(**kwargs)
        context['utdt'] = datetime.datetime.utcnow().replace(tzinfo=pytz.utc)
        context['planets'] = Planet.objects.all()
        context['pdict'] = get_all_planets(context['utdt'])
        return context

class PlanetDetailView(DetailView):
    model = Planet
    template_name = 'planet_detail.html'

    def get_context_data(self, **kwargs):
        context = super(PlanetDetailView, self).get_context_data(**kwargs)
        obj = self.get_object()
        context = deal_with_cookie(self.request, context) 
        # Replace this after testing
        utdt_start = context['utdt_start']
        utdt_end = context['utdt_end']
        location = context['location']
        planets = get_all_planets(utdt_start, utdt_end=utdt_end, location=location)
        pdict = context['planet'] = planets[obj.name]
        pdict['name'] = obj.name
        flipped =  obj.name in ['Mars', 'Jupiter', 'Saturn', 'Uranus', 'Neptune']
        # IF there are objects within 0.5° set fov to that
        sep = None
        #if obj.name not in ['Uranus', 'Neptune']: # too small to do this
        #    for nearby in pdict['close_to']:
        #        if nearby[1] <= 0.5:
        #            sep = math.radians(nearby[1])
        #            print ("Sep now: ", sep)
        if sep:
            context['view_image'] = create_planet_image(
                pdict, 
                utdt=utdt_start, 
                other_planets=planets, 
                flipped=flipped,
                min_sep = sep
            )
        else:
            context['view_image'] = create_planet_image(
                pdict, 
                utdt=utdt_start,  
                flipped=flipped
            )
        fov = 8. if obj.name in ['Uranus', 'Neptune'] else 20.
        mag_limit = 9. if obj.name in ['Uranus', 'Neptune'] else 6.5
        context['finder_chart'] = create_planet_image(
            pdict, 
            utdt=utdt_start, 
            fov=fov, 
            mag_limit=mag_limit, 
            finder_chart=True, 
            other_planets=planets
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
        # Replace after testing
        utdt_start = context['utdt_start']
        utdt_end = context['utdt_end']
        location = context['location']

        planets = get_all_planets(utdt_start, utdt_end=utdt_end, location=location)
        pdict = context['planet'] = get_moon(utdt_start, utdt_end=utdt_end, location=location)
        pdict['name'] = 'Moon'
        context['view_image'] = create_planet_image(pdict, utdt=utdt_start)
        fov = 8. if pdict['name'] in ['Uranus', 'Neptune'] else 20.
        mag_limit = 9. if pdict['name'] in ['Uranus', 'Neptune'] else 6.5
        context['finder_chart'] = create_planet_image(
            pdict, 
            utdt=utdt_start, 
            fov=fov, 
            mag_limit=mag_limit, 
            finder_chart=True, 
            other_planets=planets
        )
        return context

class AsteroidListView(ListView):
    model = Asteroid
    template_name = 'asteroid_list.html'

    def get_context_data(self, **kwargs):
        context = super(AsteroidListView, self).get_context_data(**kwargs)
        context = deal_with_cookie(self.request, context)
        # Replace after testing
        utdt_start = context['utdt_start']
        utdt_end = context['utdt_end']
        location = context['location']
        # Skip re-calculating the asteroid list if we can avoid it...
        if 'visible_asteroids' in context.keys():
            context['asteroid_list'] = [
                get_asteroid(utdt_start, x, utdt_end=utdt_end, location=location) 
                for x in Asteroid.objects.filter(slug__in=context['visible_asteroids'])
            ]
        else:
            context['asteroid_list'] = get_all_asteroids(utdt_start, utdt_end=utdt_end, location=location)
        return context

class AsteroidDetailView(DetailView):
    model = Asteroid
    template_name = 'asteroid_detail.html'

    def get_context_data(self, **kwargs):
        context = super(AsteroidDetailView, self).get_context_data(**kwargs)
        object = self.get_object()
        context = deal_with_cookie(self.request, context)
        utdt_start = context['utdt_start']
        utdt_end = context['utdt_end']
        location = context['location']
        context['asteroid'] = data = get_asteroid(utdt_start, object, utdt_end=utdt_end, location=location)
        fov = 10.
        #mag_limit = data['observe']['apparent_mag'] + 0.5
        mag_limit = 10
        context['finder_chart'] = create_planet_image(
            data, 
            utdt=utdt_start, 
            fov=fov, 
            mag_limit=mag_limit, 
            finder_chart=True, 
        )
        return context

### These are still in development.

class PlanetTrackView(DetailView):
    """
    TBD: create a map showing the motion of a planet (or other object)
    against the background stars.

    See: https://rhodesmill.org/skyfield/example-plots.html for an 
    example with Venus
    """
    model = Planet
    template_name = 'planet_track.html'

    def get_context_data(self, **kwargs):
        context = super(PlanetTrackView, self).get_context_data(**kwargs)
        planet = self.get_object()
        params = self.request.GET
        if 'utdt' not in params.keys():
            utdt = datetime.datetime(2022, 4, 10, 0, 0).replace(tzinfo=pytz.utc)
        context['utdt'] = utdt

        #utdt, planet=None, offset_before=-60, offset_after=61, step_days=5, mag_limit=5.5, fov=20
        context['track_image'] = plot_track(
            utdt, 
            planet=planet, 
            offset_before = -10,
            offset_after = 10,
            step_days = 1,
            fov=30,
            dsos=False
        )
        return context

class OrreryView(TemplateView):
    template_name = 'orrery_view.html'

    def get_context_data(self, **kwargs):
        context = super(OrreryView, self).get_context_data(**kwargs)
        params = self.request.GET
        if 'date' in params.keys():  # Processing the form
            utdt = parse_to_datetime(params['date'] + ' ' + params['time']).replace(tzinfo=pytz.utc)
            initial = {'date': params['date'], 'time': params['time']}
        else: # process the query string
            if 'utdt' in params.keys():
                utdt = parse_to_datetime(params['utdt'][0]).replace(tzinfo=pytz.utc)
            else: 
                utdt = datetime.datetime.utcnow().replace(tzinfo=pytz.utc)
            initial = {'date': utdt.strftime("%Y-%m-%d"), 'time': utdt.strftime("%H-%M")}
        
        context['utdt'] = utdt
        planets = get_ecliptic_positions(utdt)
        context['system_image'] = plot_ecliptic_positions(planets)
        context['planets'] = planets
        # Ugh this is from the Earth's perspective!  Oops!
        ### Use the distance, and ecliptic coordinates to plot the planets
        return context

