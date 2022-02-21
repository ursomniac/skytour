from skyfield.api import load, Star
from ..site_parameter.helpers import find_site_parameter
from .models import Planet, Asteroid, Comet
from .position import get_object_metadata
from .vocabs import PLANETS

def get_adjacent_planets(planet_dict, utdt):
   """
   How close are planets to each other?
   Return a tuple of (planet1, planet2, separation) if separated by < min_sep.
   """
   min_sep = find_site_parameter('adjacent-planets-separation', default=10., param_type='float')

   ts = load.timescale()
   eph = load('de421.bsp')
   earth = eph['earth']
   t = ts.utc(utdt)

   close_by = []
   # Seed the planet_dict with the target values so we only do this once.
   for planet in PLANETS:
      ra = planet_dict[planet]['apparent']['equ']['ra']
      dec = planet_dict[planet]['apparent']['equ']['dec']
      target = earth.at(t).observe(Star(ra_hours=ra, dec_degrees=dec))
      planet_dict[planet]['target'] = target
   for planet in PLANETS:
      rest = PLANETS[PLANETS.index(planet)+1:]
      p1t = planet_dict[planet]['target']
      for other_planet in rest:
         p2t = planet_dict[other_planet]['target']
         sep = p1t.separation_from(p2t).degrees.item()
         if sep <= min_sep:
            t = (planet, other_planet, sep)
            close_by.append(t)
   return close_by


def get_planet_positions(utdt, utdt_end=None, location=None):
    """
    Create the dict for all the planet positions at a given UTDT
    """
    planets = Planet.objects.order_by('pk')
    planet_dict = {}
    for p in planets:
        d = get_object_metadata(utdt, p.target, 'planet', utdt_end=utdt_end, instance=p, location=location)
        d['slug'] = p.slug
        d['name'] = p.name
        planet_dict[p.name] = d
    return planet_dict

def get_visible_asteroid_positions(utdt, utdt_end=None, location=None):
   # Actual magnitude of asteroid - if fainter than this, don't add to the list.
   mag_limit = find_site_parameter('asteroid-magnitude-limit', default=10, param_type='float')
   # Cutoff is the magnitude that an asteroid COULD get based on orbital elements.
   # This is just to limit the queryset so that we're not calculating orbital elements for 
   # hundreds of asteroids, when we'll only be interested in ~20 tops.
   cutoff = find_site_parameter('asteroid-cutoff', default=10.0, param_type='float')

   asteroids = Asteroid.objects.filter(est_brightest__lte=cutoff)
   asteroid_list = []
   for a in asteroids:
      x = get_object_metadata(utdt, None, 'asteroid', utdt_end=utdt_end, instance=a, location=location)
      if x is None:
         continue
      mag = x['observe']['apparent_magnitude']
      x['name'] = f'{a.number}: {a.name}'
      x['slug'] = a.slug
      x['number'] = a.number
      if mag <= mag_limit:
         asteroid_list.append(x)
   return asteroid_list

def get_comet_positions(utdt, utdt_end=None, location=None):
    comets = Comet.objects.filter(status=1)
    comet_list = []
    for c in comets:
        d = get_object_metadata(utdt, c.name, 'comet', utdt_end=utdt_end, instance=c, location=location)
        d['pk'] = c.pk
        d['name'] = c.name
        comet_list.append(d)
    return comet_list
