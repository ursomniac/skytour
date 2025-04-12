import datetime, time
from django.db.models import Q
from skyfield.api import load, Star
from skyfield.constants import GM_SUN_Pitjeva_2005_km3_s2 as GM_SUN
from skyfield.data import mpc
from ..site_parameter.helpers import find_site_parameter, get_ephemeris
from .asteroids import fast_asteroid
from .models import Planet, Asteroid, Comet
from .position import get_object_metadata
from .vocabs import PLANETS

def compile_nearby_planet_list(p, pdict, utdt, times=None):
   """
   Find planets near to each other in the sky.
   Default for "near" is 10°.
   """
   near_to_me = []
   
   adj_list, times = get_adjacent_planets(pdict, utdt, times=times)
   if times is not None:
          times.append((time.perf_counter(), 'Get Adjacent Planets'))

   for adj in adj_list:
      if p == adj[0]:
         near_to_me.append((adj[1], adj[2]))
      elif p == adj[1]:
         near_to_me.append((adj[0], adj[2]))
   return near_to_me, times

def get_adjacent_planets(planet_dict, utdt, times=None):
   """
   How close are planets to each other?
   Return a tuple of (planet1, planet2, separation) if separated by < min_sep.
   """
   min_sep = find_site_parameter('adjacent-planets-separation', default=10., param_type='float')

   ts = load.timescale()
   eph = load(get_ephemeris())
   earth = eph['earth']
   t = ts.utc(utdt)

   close_by = []
   # Seed the planet_dict with the target values so we only do this once.
   for planet in PLANETS:
      ra = planet_dict[planet]['apparent']['equ']['ra']
      dec = planet_dict[planet]['apparent']['equ']['dec']
      target = earth.at(t).observe(Star(ra_hours=ra, dec_degrees=dec))
      planet_dict[planet]['target'] = target
   if times is not None:
      times.append((time.perf_counter(), 'Seed Planet dict'))

   for planet in PLANETS:
      rest = PLANETS[PLANETS.index(planet)+1:]
      p1t = planet_dict[planet]['target']
      for other_planet in rest:
         p2t = planet_dict[other_planet]['target']
         sep = p1t.separation_from(p2t).degrees.item()
         if sep <= min_sep:
            t = (planet, other_planet, sep)
            close_by.append(t)
   if times is not None:
      times.append((time.perf_counter(), 'Get Planet Separations'))
   return close_by, times


def get_planet_positions(utdt, location=None):
   """
   Create the dict for all the planet positions at a given UTDT
   """
   planets = Planet.objects.order_by('pk')
   planet_dict = {}
   for p in planets:
      d = get_object_metadata(
         utdt, 
         p.target, 
         'planet', 
         instance=p, 
         location=location,
      )
      d['slug'] = p.slug
      d['name'] = p.name
      planet_dict[p.name] = d
   return planet_dict

def get_visible_asteroid_positions(utdt=None, location=None, pluto=True):
   """
   Get dict of all selected asteroids.
   Asteroids are filtered by magnitude.
   Asteroids with "always_include" set to True are not filtered.  This is generally
   set for the dwarf planets.
   """
   utdt = datetime.datetime.now(datetime.timezone.utc) if utdt is None else utdt
   # TODO V2.x: fix this somehow
   # Actual magnitude of asteroid - if fainter than this, don't add to the list.
   mag_limit = find_site_parameter('asteroid-magnitude-limit', default=10, param_type='float')
   # Cutoff is the magnitude that an asteroid COULD get based on orbital elements.
   # This is just to limit the queryset so that we're not calculating orbital elements for 
   # hundreds of asteroids, when we'll only be interested in ~20 tops.
   cutoff = find_site_parameter('asteroid-cutoff', default=10.0, param_type='float')

   ts = load.timescale()
   eph = load(get_ephemeris())
   sun = eph['sun']

   t = ts.utc(utdt)
   earth = eph['earth']
   r_earth_sun = earth.at(t).observe(sun).radec()[2].au.item()

   asteroids = Asteroid.objects.filter(Q(est_brightest__lte=cutoff) | Q(always_include=True))

   #with load.open('generated_data/bright_asteroids.txt') as f:
   #   mps = mpc.load_mpcorb_dataframe(f)
   #mps = mps.set_index('designation', drop=False)

   asteroid_list = []
   times = [(time.perf_counter(), 'Start')]
   for a in asteroids:
      mag = None
      try:
         row = a.mpc_object
         #try:
         #   row = mps.loc[a.mpc_lookup_designation]
         #except:
         #   continue
         target = sun + mpc.mpcorb_orbit(row, ts, GM_SUN)
      except Exception as err:
         o = a.mpc_object
         e = o['eccentricity']
         print(f"Error with {a}, e = {e} {type(e)}\n{err}")

      mag = fast_asteroid(a, target, t, earth, sun, r_earth_sun)
      if mag is not None and mag <= mag_limit or a.always_include:
         x = get_object_metadata(
            utdt, 
            target, 
            'asteroid', 
            instance=a, 
            location=location,
         )
         if x is None:
            continue
         x['name'] = f'{a.number}: {a.name}'
         x['slug'] = a.slug
         x['number'] = a.number
         asteroid_list.append(x)
         times.append((time.perf_counter(), x['name']))
   return asteroid_list, times

def get_comet_positions(utdt=None, location=None, times=None):
   """
   Get positions of selected comets (i.e., those whose status == 1)
   """
   utdt = datetime.datetime.now(datetime.timezone.utc) if utdt is None else utdt
   mag_limit = find_site_parameter('comet-magnitude-limit', 12.0, 'float')
   comets = Comet.objects.filter(status=1)
   comet_list = []
   for c in comets:
      d = get_object_metadata(
         utdt, 
         c.name, 
         'comet', 
         instance=c, 
         location=location,
      )
      if d is None:
         continue
      app_mag = d['observe']['apparent_magnitude']
      if app_mag > mag_limit and c.override_limits != 1:
         continue
      d['pk'] = c.pk
      d['name'] = c.name
      comet_list.append(d)
      if times is not None:
         times.append((time.perf_counter(), f"added comet {c}"))
   return comet_list, times
