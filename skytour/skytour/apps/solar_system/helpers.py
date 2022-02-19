from ..site_parameter.helpers import find_site_parameter
from .models import Asteroid, Planet
from .asteroids import get_asteroid
from .planets import get_solar_system_object
from .vocabs import PLANETS

def assemble_asteroid_list(utdt, slugs=None):
   if not slugs:
      return None
   objects = Asteroid.objects.filter(slug__in=slugs)
   alist = []
   for o in objects:
      a = get_asteroid(utdt, o)
      alist.append(a)
   return alist

def get_visible_asteroids(utdt, utdt_end=None, location=None, serialize=False, debug=False):
   """
   utdt = when we're observing
   utdt_end = when we're planning to stop observing, if not None then we return alt/az for
      the entire session
   location = ObservingLocation - used to get LAST/alt/az.
   """
   # Actual magnitude of asteroid - if fainter than this, don't add to the list.
   mag_limit = find_site_parameter('asteroid-magnitude-limit', default=10, param_type='float')

   # Cutoff is the magnitude that an asteroid COULD get based on orbital elements.
   # This is just to limit the queryset so that we're not calculating orbital elements for 
   # hundreds of asteroids, when we'll only be interested in ~20 tops.
   cutoff = find_site_parameter('asteroid-cutoff', default=10.0, param_type='float')

   asteroids = Asteroid.objects.filter(est_brightest__lte=cutoff)
   asteroid_list = []
   for a in asteroids:
      try:
         this_asteroid = get_asteroid(utdt, a, utdt_end=utdt_end, location=location, serialize=serialize)
      except:
         continue # no asteroid returned for some reason, skip
      mag = this_asteroid['observe']['apparent_mag'] 
      if mag <= mag_limit:
         asteroid_list.append(this_asteroid)
      else:
         if debug:
            print ("{} is too faint {}".format(a, mag))
   return asteroid_list

def get_all_planets(utdt, utdt_end=None, location=None):
    """
    Get a list of all the planet dicts for a given UTDT.
    if utdt_end and location are given return alt/az/etc. information.
    """
    planet_dict = get_planet_dict(utdt, utdt_end=utdt_end, location=location)
    adjacent_planets = get_adjacent_planets(planet_dict)
    for p1, p2, sep in adjacent_planets:
        planet_dict[p1]['close_to'].append(tuple([p2, sep]))
        planet_dict[p2]['close_to'].append(tuple([p1, sep]))
    return planet_dict

def get_adjacent_planets(planets=None, utdt=None):
    """
    How close are planets to each other?
    Return a tuple of (planet1, planet2, separation) if separated by < min_sep.
    """
    min_sep = find_site_parameter('adjacent-planets-separation', default=10., param_type='float')
    if not planets:
        planets = get_planet_dict(utdt)
    close_by = []
    for planet in PLANETS:
        rest = PLANETS[PLANETS.index(planet)+1:]
        for other_planet in rest:
            p1t = planets[planet]['target']
            p2t = planets[other_planet]['target']
            sep = p1t.separation_from(p2t).degrees.item()
            if sep <= min_sep:
                t = (planet, other_planet, sep)
                close_by.append(t)
    return close_by

def get_planet_dict(utdt, utdt_end=None, location=None):
    planet_dict = {}
    for name in PLANETS:
        p = Planet.objects.get(name=name)
        planet = get_solar_system_object(utdt, p, utdt_end=utdt_end, location=location)
        planet_dict[name] = planet
    return planet_dict
