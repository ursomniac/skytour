import datetime
import pytz
from skyfield.api import wgs84, load
from ..dso.models import DSO
from ..solar_system.moon import get_moon
from ..solar_system.plot import create_planet_image
from ..solar_system.planets import get_all_planets, is_planet_up
from ..solar_system.sun import get_sun
from ..utils.format import to_sex
from .old_almanac import dark_time
from .local import get_observing_situation
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
    moon = get_moon(utdt_start, location=location, sun=sun) # dict of stuff
    # update the dict with local observing situation
    moon = get_observing_situation(moon, utdt_start, utdt_end, location) # altaz, etc.
    context['moon'] = moon

    ### Planets
    planet_data_dict = get_all_planets(utdt_start, location=location)

    ccc = False
    if ccc:
    # OK - which planets are up in the observing window?
        planets = []
        for planet, data in planet_data_dict.items():
            coord = data['target'].radec()
            ra = coord[0].hours
            dec = coord[1].degrees
            distance = coord[2]

            pdict = {}
            #pdict['name'] = planet.title()
            #pdict['ra'] = to_sex(ra, format='ra')
            #pdict['dec'] = to_sex(dec, format='dec')
            #pdict['dist_au'] = "{:.4f} AU".format(distance.au)
            #pdict['dist_km'] = "{:,.2f} km".format(distance.km)
            #pdict['dist_mi'] = "{:,.2f} mi".format(distance.km/1.609)
            #light_time = data['target'].light_time.item()
            #pdict['light_time'] = to_sex(light_time * 24., format='hms') # hours
            #pdict['angular_size'] = get_angular_size(DIAMETERS[planet.title()], distance.km)
            #pdict['illum_fraction'] = data['physical']['illum_fraction'] * 100.
            #pdict['phase_angle'] = to_sex(data['physical']['phase_angle'], format='degrees')


            for k, v in [('start', utdt_start), ('end', utdt_end)]:
                pdict[k] = {}
                az, alt, is_up = is_planet_up(v, location, ra, dec, min_alt=0.)
                pdict[k]['azimuth'] = to_sex(az, format='degrees')
                pdict[k]['altitude'] = to_sex(alt, format='dec')
                pdict[k]['is_up'] = is_up

            # Plots
            pdict['view_image'] = create_planet_image(planet, data, utdt=utdt_start)
            if pdict['name'] in ['Uranus', 'Neptune']:
                pdict['finder_chart'] = create_planet_image(planet, data, utdt=utdt_start, finder_chart=True)
            else:
                pdict['finder_chart'] = create_planet_image(
                    planet, 
                    data, 
                    utdt=utdt_start,
                    fov=20,
                    mag_limit=6.5,
                    finder_chart=True
                )

            planets.append(pdict)
    context['planets'] = []

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

