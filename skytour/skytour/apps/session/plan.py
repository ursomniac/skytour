import datetime, pytz
from skyfield.api import wgs84, load
from ..dso.models import DSO
from ..observe.almanac import dark_time
from ..observe.models import ObservingLocation
from ..observe.time import get_julian_date, get_t_epoch
from ..solar_system.asteroids import get_all_asteroids
from ..solar_system.moon import get_moon
from ..solar_system.plot import create_planet_image
from ..solar_system.planets import get_all_planets
from ..solar_system.sun import get_sun
from ..solar_system.vocabs import PLANETS

def get_plan(form, debug=False):
    """
    This creates an observing plan for a UTDT and location.
         - get meta information from the form
         - generate the planet dicts
            - if a planet will be above the horizon within the session, show
                the telescope view with moons or phase
        - generate a list of DSOs organized by priority
    """
    # Sort out the form's date and time and time_zone fields
    if debug:
        context = {}
        location = context['location']= ObservingLocation.objects.get(pk=43)
        utdt_start = context['utdt_start'] = datetime.datetime.utcnow().replace(tzinfo=pytz.utc)
        session_length = datetime.timedelta(hours=4)
        context['show_planets'] = 'all'
        context['dec_limit'] = 20.
        context['mag_limit'] = 12.0
    else:
        context = form.cleaned_data
        location = ObservingLocation.objects.get(pk=context['location'].pk)
        ### Preliminaries
        if context['set_to_now'] == 'Yes':
            utdt_start = context['utdt_start'] = datetime.datetime.utcnow().replace(tzinfo=pytz.utc)
        else:
            utdt_start = context['utdt_start'] = datetime.datetime.combine(context['date'], context['time']).replace(tzinfo=pytz.utc)
        session_length = datetime.timedelta(hours=context['session_length'])
    utdt_end = context['utdt_end'] = utdt_start + session_length
    context['julian_date'] = get_julian_date(utdt_start)
    t = context['t'] = get_t_epoch(context['julian_date'])

    # Observing Location
    context['location'] = location
    context['latitude'] = location.latitude   # degrees
    context['longitude'] = location.longitude # degrees, positive East (ugh)

    # Preliminaries
    context['ts'] = load.timescale()
    context['wgs'] = wgs84.latlon(location.latitude, location.longitude)
    context['eph'] = load('de421.bsp')

    ### Astronomical Twilight
    (twi_end, twi_begin) = dark_time(context)
    context['twilight_end'] = twi_end.utc_datetime()
    context['twilight_begin'] = twi_begin.utc_datetime()

    ### Sun
    sun = get_sun(utdt_start, location=location, eph=context['eph']) # this should be a dict too.

    ### Moon
    moon = get_moon(utdt_start, utdt_end=utdt_end, location=location, sun=sun) # dict of stuff
    moon['view_image'] = create_planet_image(moon, utdt=utdt_start)
    # update the dict with local observing situation
    context['moon'] = moon
    context['show_moon'] = moon['session']['start']['is_up'] or moon['session']['end']['is_up'] or context['show_planets']

    ### Planets
    planet_data_dict = get_all_planets(utdt_start, utdt_end=utdt_end, location=location)

    # OK - which planets are up in the observing window?
    planets = []
    for k in PLANETS:
        pd = planet_data_dict[k]
        # RAD 12 Jan 2022 - don't get planet images to save time
        go = True if context['show_planets'] == 'all' or pd['session']['start']['is_up'] or pd['session']['end']['is_up'] else False
        pd['show_planet'] = go
        #if go:
        #    pd['view_image'] = create_planet_image(pd, utdt=utdt_start)
        planets.append(pd)
    context['planets'] = planets

    ### Asteroids
    asteroids = get_all_asteroids(utdt_start, utdt_end=utdt_end, location=location)
    for v in asteroids:
        go = True if v['session']['start']['is_up'] or v['session']['end']['is_up'] else False
        v['show_asteroid'] = go
    context['asteroids'] = asteroids

    ### DSO List
    targets = {}
    all_dsos = DSO.objects.filter(
        dec__gt=context['dec_limit'], 
        magnitude__lt=context['mag_limit']
    ).order_by('ra')
    for dso in all_dsos:
        if dso.object_is_up(location, context['utdt_start'], min_alt=20.) \
                or dso.object_is_up(location, context['utdt_end'], min_alt=0.):
            priority = dso.priority.lower()
            if priority in targets.keys():
                targets[priority].append(dso)
            else:
                targets[priority] = [dso]
    context['dso_targets'] = targets
    return context # everything in {{ plan."things" }}
