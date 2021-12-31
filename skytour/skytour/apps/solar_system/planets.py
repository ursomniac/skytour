import math
from matplotlib.pyplot import get
from skyfield.api import load
from skyfield.almanac import (
    phase_angle as get_phase_angle, 
    fraction_illuminated,
    moon_phase
)
from skyfield.magnitudelib import planetary_magnitude
from ..observe.almanac import get_object_rise_set
from ..utils.compile import observe_to_values
from ..utils.transform import get_alt_az
#from .saturn import saturn_ring
from .utils import get_angular_size, get_plotting_phase_angle
from .vocabs import PLANET_DICT

def get_solar_system_object(utdt, name, location=None):
    ts = load.timescale()
    t = ts.utc(utdt.year, utdt.month, utdt.day, utdt.hour, utdt.minute)
    eph = load('de421.bsp')
    earth = eph['earth']

    if name not in PLANET_DICT.keys():
        return None

    pdict = PLANET_DICT[name]
    target = pdict['target']
    obs = earth.at(t).observe(target)
    sun = earth.at(t).observe(eph['sun'])

    # Get things from almanac
    k = fraction_illuminated(eph, target, t).item() # float
    i = get_phase_angle(eph, target, t).item() # degrees
    ang_size = get_angular_size(
        pdict['diameter'], 
        obs.radec()[2].km
    ) # diameter in arcsec
    plotting_phase_angle = get_plotting_phase_angle(obs, sun)
    
    # apparent magnitude
    try:
        mag = planetary_magnitude(obs).item()
    except:
        mag = None

    # deal with moons
    moon_list = pdict['moon_list']
    moon_obs = []
    if moon_list:
        # we have moons!
        moonsys = load(pdict['load'])
        earth_s = moonsys['earth']
        for moon in moon_list:
            mdict = {}
            mdict['name'] = moon
            moon_target = moonsys[moon]
            mdict['target'] = earth_s.at(t).observe(moon_target)
            moon_obs.append(mdict)
    else:
        moon_obs = None

    almanac = get_object_rise_set(utdt, eph, target, location) if location else None

    return {
        'target': obs,
        'coords': observe_to_values(obs),
        'observe': {
            'illum_fraction': k,
            'apparent_mag': mag,
            'angular_diameter': ang_size,
            'phase_angle': i,
            'plotting_phase_angle':  plotting_phase_angle
            # elongation
            # position_angle
        },
        'almanac': almanac,
        'moons': moon_obs
    }

def is_planet_up(utdt, location, ra, dec, min_alt=0.):
    az, alt = get_alt_az(utdt, location.latitude, location.longitude, ra, dec)
    up = alt > min_alt
    return az, alt, up

def get_all_planets(utdt, location=None):
    planet_dict = {}
    for name in PLANET_DICT.keys():
        planet = get_solar_system_object(utdt, name, location=location)
        planet_dict[name] = planet
    return planet_dict