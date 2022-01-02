import math
from matplotlib.pyplot import get
from skyfield.api import load 
from skyfield.almanac import (
    phase_angle as get_phase_angle, 
    fraction_illuminated,
)
from skyfield.magnitudelib import planetary_magnitude
from ..observe.almanac import get_object_rise_set
from ..observe.local import get_observing_situation
from ..utils.compile import observe_to_values
from ..utils.format import to_sex
from .utils import get_constellation

#from .saturn import saturn_ring
from .models import Planet
from .utils import get_angular_size, get_plotting_phase_angle, get_elongation
from .vocabs import PLANETS

def get_solar_system_object(utdt, name, utdt_end=None, location=None):
    ts = load.timescale()
    t = ts.utc(utdt.year, utdt.month, utdt.day, utdt.hour, utdt.minute)
    eph = load('de421.bsp')
    earth = eph['earth']

    planet = Planet.objects.filter(name=name).first()
    if not planet:
        return None

    obs = earth.at(t).observe(eph[planet.target])
    (obs_ra, obs_dec, obs_distance) = obs.radec()
    constellation = get_constellation(obs_ra.hours.item(), obs_dec.degrees.item())
    sun = earth.at(t).observe(eph['sun'])

    almanac = get_object_rise_set(utdt, eph, eph[planet.target], location) if location else None
    session = get_observing_situation(obs, utdt, utdt_end, location) if utdt_end and location else None

    # Get things from almanac
    # i = phase angle
    i = get_phase_angle(eph, planet.target, t).degrees.item() # degrees
    ang_size = get_angular_size(planet.diameter, obs.radec()[2].km) # diameter in arcsec
    elongation = get_elongation(obs, sun)
    plotting_phase_angle = get_plotting_phase_angle(name, i, elongation)
    # k = illuminated fraction of the Moon's disk
    k = fraction_illuminated(eph, planet.target, t).item() # float

    # apparent magnitude
    try:
        mag = planetary_magnitude(obs).item()
    except:
        mag = None

    # deal with moons
    moon_list = planet.moon_list
    moon_obs = []
    if moon_list:
        # we have moons!
        moonsys = load(planet.load)
        earth_s = moonsys['earth']
        for moon in moon_list:
            mdict = {}
            mdict['name'] = moon
            moon_target = moonsys[moon]
            mdict['target'] = earth_s.at(t).observe(moon_target)
            moon_obs.append(mdict)
    else:
        moon_obs = None

    return {
        'name': name,
        'slug': planet.slug,
        'target': obs,
        'coords': observe_to_values(obs),
        'observe': {
            'constellation': constellation,
            'illum_fraction': k * 100.,  # percent
            'apparent_mag': mag,
            'angular_diameter': ang_size,
            'angular_diameter_str': to_sex(ang_size/3600., format='degrees'),
            'phase_angle': i,
            'phase_angle_str': to_sex(i, format="degrees"),
            'plotting_phase_angle':  plotting_phase_angle,
            'elongation': elongation
            # position_angle
        },
        'almanac': almanac,
        'session': session,
        'moons': moon_obs
    }

def get_all_planets(utdt, utdt_end=None, location=None):
    planet_dict = {}
    for name in PLANETS:
        planet = get_solar_system_object(utdt, name, utdt_end=utdt_end, location=location)
        planet_dict[name] = planet
    return planet_dict