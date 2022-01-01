import datetime
import pytz
from skyfield.api import wgs84, load
from ..dso.models import DSO
from ..solar_system.moon import get_moon
from ..solar_system.plot import create_planet_image
from ..solar_system.planets import get_all_planets
from ..solar_system.sun import get_sun
from ..solar_system.vocabs import PLANETS
from ..utils.format import to_sex
from .almanac import dark_time
from .models import ObservingLocation
from .time import get_julian_date, local_time_to_utdt, get_local_datetime, get_t_epoch


def get_plan(form, debug=False):
    # Sort out the form's date and time and time_zone fields
    if debug:
        context = {}
        location = context['location']= ObservingLocation.objects.get(pk=43)
        utdt_start = context['utdt'] = datetime.datetime(2021, 12, 23, 1, 0, 0, tzinfo=pytz.utc)
        session_length = datetime.timedelta(hours=4)
    else:
        context = form.cleaned_data
        location = ObservingLocation.objects.get(pk=context['location'].pk)
        ### Preliminaries
        # This might or might not be a local time.
        local_time = get_local_datetime(context['date'], context['time'], context['time_zone'])
        utdt_start = context['utdt'] = local_time_to_utdt(local_time)
        session_length = datetime.timedelta(hours=context['session_length'])
    utdt_end = context['utdt_end'] = utdt_start + session_length
    context['julian_date'] = get_julian_date(utdt_start)
    t = context['t'] = get_t_epoch(context['julian_date'])

    # Observing Location
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

    ### Planets
    planet_data_dict = get_all_planets(utdt_start, utdt_end=utdt_end, location=location)

    # OK - which planets are up in the observing window?
    planets = []
    for k in PLANETS:
        pd = planet_data_dict[k]
        pd['name'] = k
        pd['view_image'] = create_planet_image(pd, utdt=utdt_start)
        #if k in ['Uranus', 'Neptune']:
        #    pd['finder_chart'] = create_planet_image(
        #        pd, 
        #        utdt=utdt_start, 
        #        other_planets=planet_data_dict, 
        #        fov=8,
        #        finder_chart=True
        #    )
        #else:
        #    pd['finder_chart'] = create_planet_image(
        #        pd, 
        #        utdt=utdt_start, 
        #        other_planets=planet_data_dict, 
        #        fov=20, 
        #        mag_limit=6.5, 
        #        finder_chart=True
        #    )
        planets.append(pd)
    context['planets'] = planets

    ### DSO List
    targets = {}
    all_dsos = DSO.objects.filter(
        dec__gt=context['dec_limit'], 
        magnitude__lt=context['mag_limit']
    ).order_by('ra')
    for dso in all_dsos:
        if dso.object_is_up(location, context['utdt'], min_alt=20.) \
                or dso.object_is_up(location, context['utdt_end'], min_alt=0.):
            priority = dso.priority.lower()
            if priority in targets.keys():
                targets[priority].append(dso)
            else:
                targets[priority] = [dso]
    context['targets'] = targets

    return context # everything in {{ plan."things" }}
