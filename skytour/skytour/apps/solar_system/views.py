import datetime, pytz
from dateutil.parser import parse as parse_to_datetime
from django.views.generic.base import TemplateView
from django.views.generic.detail import DetailView
from django.views.generic.edit import FormView
from django.views.generic.list import ListView
from ..session.cookie import deal_with_cookie, get_cookie #, update_cookie_with_asteroids
from .asteroids import get_asteroid
from .helpers import get_visible_asteroids
from .comets import get_comet
from .forms import TrackerForm
from .helpers import get_all_planets
from .models import Comet, Planet, Asteroid
from .moon import get_moon
from .planets import get_ecliptic_positions
from .plot import create_planet_image, plot_ecliptic_positions, plot_track, get_planet_map

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
        # This is where we start rebuilding...
        context['planet'] = planets_cookie[obj.name]
        #planets = get_all_planets(utdt_start, utdt_end=utdt_end, location=location)
        #pdict = context['planet'] = planets[obj.name]
        #pdict['name'] = obj.name
        
        context['view_image'] = create_planet_image(
            pdict, 
            utdt=context['utdt_start'],  
            flipped=flipped,
            reversed=reversed
        )
        
        # TODO: Put this in site-parameters?
        fov = 8. if obj.name in ['Uranus', 'Neptune'] else 20.
        mag_limit = 9. if obj.name in ['Uranus', 'Neptune'] else 6.5
        other_asteroids = None

        context['finder_chart'] = create_planet_image(
            pdict, 
            utdt=utdt_start, 
            fov=fov, 
            mag_limit=mag_limit, 
            finder_chart=True, 
            other_planets=planets_cookie,
            other_asteroids=asteroids_cookie,
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
        reversed = context['color_scheme'] == True

        # Replace after testing
        utdt_start = context['utdt_start']
        utdt_end = context['utdt_end']
        location = context['location']

        planets = get_all_planets(utdt_start, utdt_end=utdt_end, location=location)
        pdict = context['planet'] = get_moon(utdt_start, utdt_end=utdt_end, location=location)
        pdict['name'] = 'Moon'
        context['view_image'] = create_planet_image(pdict, utdt=utdt_start, reversed=reversed)
        fov = 8. if pdict['name'] in ['Uranus', 'Neptune'] else 20.
        mag_limit = 9. if pdict['name'] in ['Uranus', 'Neptune'] else 6.5
        context['finder_chart'] = create_planet_image(
            pdict, 
            utdt=utdt_start, 
            fov=fov, 
            mag_limit=mag_limit, 
            finder_chart=True, 
            other_planets=planets,
            reversed=reversed
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
        #if 'visible_asteroids' in context.keys():
        #    context['asteroid_list'] = [
        #        get_asteroid(utdt_start, x, utdt_end=utdt_end, location=location) 
        #        for x in Asteroid.objects.filter(slug__in=context['visible_asteroids'])
        #    ]
        #else:
        #    context['asteroid_list'] = get_visible_asteroids(utdt_start, utdt_end=utdt_end, location=location)
        #    slugs = update_cookie_with_asteroids(self.request, context['asteroid_list'])
        return context

class AsteroidDetailView(DetailView):
    model = Asteroid
    template_name = 'asteroid_detail.html'

    def get_context_data(self, **kwargs):
        context = super(AsteroidDetailView, self).get_context_data(**kwargs)
        object = self.get_object()
        context = deal_with_cookie(self.request, context)
        reversed = context['color_scheme'] == 'dark'

        utdt_start = context['utdt_start']
        utdt_end = context['utdt_end']
        location = context['location']
        context['asteroid'] = data = get_asteroid(utdt_start, object, utdt_end=utdt_end, location=location)
        other_planets = get_all_planets(utdt_start)
        other_asteroids = None
        if 'visible_asteroids' in context.keys():
            alist = Asteroid.objects.filter(slug__in=context['visible_asteroids']).exclude(slug=object.slug)
            other_asteroids = [get_asteroid(utdt_start, x) for x in alist]
        fov = 10.

        mag_limit = 10
        context['finder_chart'] = create_planet_image(
            data, 
            utdt=utdt_start, 
            other_asteroids=other_asteroids,
            other_planets=other_planets,
            fov=fov, 
            mag_limit=mag_limit, 
            finder_chart=True, 
            reversed=reversed
        )
        return context

class CometListView(ListView):
    model = Comet
    template_name = 'comet_list.html'

    def get_context_data(self, **kwargs):
        context = super(CometListView, self).get_context_data(**kwargs)
        context = deal_with_cookie(self.request, context)

        # Replace after testing
        utdt_start = context['utdt_start']
        utdt_end = context['utdt_end']
        location = context['location']
        comets = Comet.objects.filter(status=1)
        comet_list = []
        for comet in comets:
            comet_list.append(get_comet(utdt_start, comet, utdt_end=utdt_end, location=location))
        context['comet_list'] = comet_list
        return context

class CometDetailView(DetailView):
    model = Comet
    template_name = 'comet_detail.html'

    def get_context_data(self, **kwargs):
        context = super(CometDetailView, self).get_context_data(**kwargs)
        object = self.get_object()
        context = deal_with_cookie(self.request, context)
        reversed = context['color_scheme'] == 'dark'
        
        utdt_start = context['utdt_start']
        utdt_end = context['utdt_end']
        location = context['location']

        context['comet'] = data = get_comet(utdt_start, object, utdt_end=utdt_end, location=location)
        other_planets = get_all_planets(utdt_start)
        other_asteroids = None
        #if 'visible_asteroids' in context.keys():
        #    alist = Asteroid.objects.filter(slug__in=context['visible_asteroids']).exclude(slug=object.slug)
        #    other_asteroids = [get_asteroid(utdt_start, x) for x in alist]
        fov = 10.
        #mag_limit = data['observe']['apparent_mag'] + 0.5
        mag_limit = 10
        context['finder_chart'] = create_planet_image(
            data, 
            utdt=utdt_start, 
            #other_asteroids=other_asteroids,
            other_planets=other_planets,
            fov=fov, 
            mag_limit=mag_limit, 
            finder_chart=True, 
            reversed=reversed
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

