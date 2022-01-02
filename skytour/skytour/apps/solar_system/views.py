import datetime, pytz
from dateutil.parser import parse as parse_to_datetime
from urllib.parse import urlencode
from django.views.generic.base import TemplateView
from django.views.generic.detail import DetailView
from django.views.generic.edit import FormView, FormMixin
from django.views.generic.list import ListView
from ..observe.models import ObservingLocation
from ..observe.time import get_julian_date
from .forms import ShowPlanetForm
from .models import Planet
from .moon import get_moon
from .planets import get_all_planets
from .plot import create_planet_image


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
    form_class = ShowPlanetForm


    def get_context_data(self, **kwargs):
        context = super(PlanetDetailView, self).get_context_data(**kwargs)
        obj = self.get_object()
        params = self.request.GET
        initial = {}
        if 'utdt_start' in params.keys(): # process the query string
            if 'utdt_start' in params.keys():
                utdt_start = parse_to_datetime(params['utdt_start']).replace(tzinfo=pytz.utc)
            if 'utdt_end' in params.keys():
                utdt_end = parse_to_datetime(params['utdt_end']).replace(tzinfo=pytz.utc)
            if 'location' in params.keys():
                loc_pk = params['location']
            initial = {'date': utdt_start.strftime("%Y-%m-%d"), 'time': utdt_start.strftime("%H:%M"), 'location': loc_pk}
        elif 'date' in params.keys():  # Processing the form
            utdt_start = parse_to_datetime(params['date'] + ' ' + params['time']).replace(tzinfo=pytz.utc)
            utdt_end = utdt_start + datetime.timedelta(hours=3)
            loc_pk = params['location']
            initial = {'date': params['date'], 'time': params['time'], 'location': params['location']}
        else:
            utdt_start = datetime.datetime.utcnow().replace(tzinfo=pytz.utc)
            utdt_end = utdt_start + datetime.timedelta(hours=3)
            loc_pk = 43
            initial = {'date': utdt_start.strftime("%Y-%m-%d"), 'time': utdt_start.strftime("%H:%M"), 'location': loc_pk}

        obs_params = dict(
            utdt_start = utdt_start,
            utdt_end = utdt_end,
            location = loc_pk
        )
        context['query_params'] = urlencode(obs_params)

        # put it all together
        context['utdt_start'] = utdt_start
        context['utdt_end'] = utdt_end
        context['julian_date'] = get_julian_date(utdt_start)
        context['location'] = location = ObservingLocation.objects.get(pk=loc_pk)
        planets = get_all_planets(utdt_start, utdt_end=utdt_end, location=location)
        pdict = context['planet'] = planets[obj.name]
        pdict['name'] = obj.name
        context['view_image'] = create_planet_image(pdict, utdt=utdt_start)
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
        context['form'] = ShowPlanetForm(initial=initial)
        return context

class MoonDetailView(TemplateView):
    template_name = 'planet_detail.html'

    def get_context_data(self, **kwargs):
        context = super(MoonDetailView, self).get_context_data(**kwargs)
        params = self.request.GET
        if 'date' in params.keys():  # Processing the form
            utdt_start = parse_to_datetime(params['date'] + ' ' + params['time']).replace(tzinfo=pytz.utc)
            utdt_end = utdt_start + datetime.timedelta(hours=3)
            loc_pk = params['location']
            initial = {'date': params['date'], 'time': params['time'], 'location': params['location']}
        else: # process the query string
            if 'utdt_start' in params.keys():
                utdt_start = parse_to_datetime(params['utdt_start'][0]).replace(tzinfo=pytz.utc)
            else: 
                utdt_start = datetime.datetime.utcnow().replace(tzinfo=pytz.utc)
            if 'utdt_end' in params.keys():
                utdt_end = parse_to_datetime(params['utdt_end'][0]).replace(tzinfo=pytz.utc)
            else:
                utdt_end = datetime.datetime.utcnow().replace(tzinfo=pytz.utc)
                utdt_end += datetime.timedelta(hours=3)
            if 'location' in params.keys():
                loc_pk = params['location'][0]
            else:
                loc_pk = 43
            initial = {'date': utdt_start.strftime("%Y-%m-%d"), 'time': utdt_start.strftime("%H-%M"), 'location': loc_pk}

            # put it all together
        context['utdt_start'] = utdt_start
        context['utdt_end'] = utdt_end
        context['julian_date'] = get_julian_date(utdt_start)
        context['location'] = location = ObservingLocation.objects.get(pk=loc_pk)
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
        context['form'] = ShowPlanetForm(initial=initial)
        return context