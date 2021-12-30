import datetime
import pytz
from skyfield import almanac
from skyfield.api import wgs84, load
from ..meeus.almanac import get_julian_date, get_t_epoch, to_sex
from ..meeus.moon import simple_lunar_phase 
from ..skyobject.models import DSO
from ..solar_system.plot import create_planet_image
from ..solar_system.utils import get_all_planets, is_planet_up, get_sun, get_moon, get_angular_size
from ..solar_system.vocabs import DIAMETERS
from .models import ObservingLocation
from .utils import dark_time

UT_OFFSET = {
    'Universal Time': 0,
    'US/Eastern': 5,
    'US/Central': 6,
    'US/Mountain': 7,
    'US/Pacific': 8
}

def get_plan(form, debug=False):
    if debug:
        context = {}
        location = context['location']= ObservingLocation.objects.get(pk=43)
        utdt = context['utdt'] = datetime.datetime(2021, 12, 23, 1, 0, 0, tzinfo=pytz.utc)
        session_length = datetime.timedelta(hours=4)
    else:
        context = form.cleaned_data
        location = ObservingLocation.objects.get(pk=context['location'].pk)
        ### Preliminaries
        obs_time = datetime.datetime.combine(context['date'], context['time'])
        utdt = obs_time + datetime.timedelta(hours=UT_OFFSET[context['time_zone']])
        if context['dst'] == 'Yes':
            utdt += datetime.timedelta(hours=-1)
        context['utdt'] = utdt.replace(tzinfo=pytz.utc)
        session_length = datetime.timedelta(hours=context['session_length'])

    context['latitude'] = location.latitude
    context['longitude'] = location.longitude

    # Preliminaries
    context['ts'] = load.timescale()
    context['wgs'] = wgs84.latlon(location.latitude, location.longitude)
    context['eph'] = load('de421.bsp')
    utdt_end = context['utdt_end'] = context['utdt'] + session_length
    context['julian_date'] = get_julian_date(utdt)
    t = context['t'] = get_t_epoch(context['julian_date'])

    ### Astronomical Twilight
    (twi_end, twi_begin) = dark_time(context)
    context['twilight_end'] = twi_end.utc_datetime()
    context['twilight_begin'] = twi_begin.utc_datetime()

    ### Sun
    sun = get_sun(utdt) # this should be a dict too.

    ### Moon
    moon = get_moon(utdt) # dict of stuff
    (xmoon_ra, xmoon_dec, moon_distance) = moon['observe'].radec()
    moon_ra = xmoon_ra.hours.item()
    moon_dec = xmoon_dec.degrees.item()
    d_km = moon_distance.km.item()
    ang_size = get_angular_size(6378.14, d_km, units='degrees')

    d_moon = {
        'ra': to_sex(moon_ra),
        'dec': to_sex(moon_dec, format='dec'),
        'dist_au': "{:7.5f}".format(moon_distance.au.item()),
        'dist_km': "{:8.1f}".format(moon_distance.km.item()),
        'dist_mi': "{:8.1f}".format(moon_distance.km.item() / 1.609),
        'light_time': to_sex(moon_distance.light_seconds().item(), format='hours'),
        'angular_size': ang_size,
        'start': {}, 'end': {}
    }
    ### WE CAN MAKE THIS BETTER
    for k, v in [('start', utdt), ('end', utdt_end)]:
        d_moon[k] = {}
        az, alt, is_up = is_planet_up(v, location, moon_ra, moon_dec, min_alt=0.)
        d_moon[k]['azimuth'] = to_sex(az, format='degrees')
        d_moon[k]['altitude'] = to_sex(alt, format='dec')
        d_moon[k]['is_up'] = is_up
    context['moon'] = d_moon
    context['moon']['phase'] = simple_lunar_phase(context['julian_date'], return_dict=True)

    ### Planets
    planet_data_dict = get_all_planets(context['utdt'])
    # OK - which planets are up in the observing window?
    planets = []
    for planet, data in planet_data_dict.items():
        coord = data['observe'].radec()
        ra = coord[0].hours
        dec = coord[1].degrees
        distance = coord[2]

        pdict = {}
        pdict['name'] = planet.title()
        pdict['ra'] = to_sex(ra, format='ra')
        pdict['dec'] = to_sex(dec, format='dec')
        pdict['dist_au'] = "{:.4f} AU".format(distance.au)
        pdict['dist_km'] = "{:,.2f} km".format(distance.km)
        pdict['dist_mi'] = "{:,.2f} mi".format(distance.km/1.609)
        light_time = data['observe'].light_time.item()
        pdict['light_time'] = to_sex(light_time * 24., format='hms') # hours
        pdict['angular_size'] = get_angular_size(DIAMETERS[planet.title()], distance.km)
        pdict['illum_fraction'] = data['physical']['illum_fraction'] * 100.
        pdict['phase_angle'] = to_sex(data['physical']['phase_angle'], format='degrees')
        for k, v in [('start', utdt), ('end', utdt_end)]:
            pdict[k] = {}
            az, alt, is_up = is_planet_up(v, location, ra, dec, min_alt=0.)
            pdict[k]['azimuth'] = to_sex(az, format='degrees')
            pdict[k]['altitude'] = to_sex(alt, format='dec')
            pdict[k]['is_up'] = is_up

        # Plots
        pdict['view_image'] = create_planet_image(planet, data, utdt=utdt.replace(tzinfo=pytz.utc))
        if pdict['name'] in ['Uranus', 'Neptune']:
            pdict['finder_chart'] = create_planet_image(planet, data, utdt=utdt.replace(tzinfo=pytz.utc), finder_chart=True)
        else:
            pdict['finder_chart'] = create_planet_image(
                planet, 
                data, 
                utdt=utdt.replace(tzinfo=pytz.utc), 
                fov=20,
                mag_limit=6.5,
                finder_chart=True
            )

        planets.append(pdict)
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

