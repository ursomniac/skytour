import datetime, pytz
from dateutil.parser import isoparse
import time
from ..apps.observe.models import ObservingLocation
from ..apps.session.cookie import get_cookie_defaults
from ..apps.solar_system.helpers import get_planet_dict, get_visible_asteroids

def show_times(times):
    t0 = times[0][0]
    for t in times:
        dt = t[0] - t0
        print (f'{t[0]:.3f}s\t{dt:.3f} ∆t\t{t[1]}')

def get_information():
    # Start the stopwatch
    times = [(time.perf_counter(), 'Start')]

    # Get the primary metadata: UT, location
    cookie = get_cookie_defaults()
    utdt_start = isoparse(cookie['utdt_start'])
    location = ObservingLocation.objects.get(pk=cookie['location'])
    times.append((time.perf_counter(), f'Created Default Cookie'))

    # Get the Planets
    planet_dict = get_planet_dict(utdt_start, location=location)
    cookie['planet_dict'] = planet_dict
    times.append((time.perf_counter(), f'Got Planets'))

    # Get Asteroids
    asteroid_list = get_visible_asteroids(utdt_start, location=location)
    cookie['asteroid_list'] = asteroid_list
    times.append((time.perf_counter(), f'Got Asteroids'))

    ### All done - show performance
    show_times(times)
