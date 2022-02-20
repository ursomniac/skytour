
import math
from skyfield.api import load
from skyfield.almanac import (
    phase_angle as get_phase_angle, 
    fraction_illuminated,
    moon_phase
)
from ..observe.almanac import get_object_rise_set
from ..observe.local import get_observing_situation
from ..observe.time import get_julian_date
from ..utils.compile import observe_to_values
from ..utils.format import to_sex
from .utils import (
    get_angular_size, 
    get_phase_description, 
    get_constellation, 
    get_elongation
)

MOON_PHASES = [
    'NEW MOON', 'WAXING CRESCENT', 'FIRST QUARTER', 'WAXING GIBBOUS', 'FULL MOON', 
    'WANING GIBBOUS', 'LAST QUARTER', 'WANING CRESCENT', 'NEW MOON'
]

def simple_lunar_phase(jd):
    """
    This just does a quick-and-dirty estimate of the Moon's phase given the date.
    """
    lunar_period = 29.530588853
    lunations = (jd - 2451550.1) / lunar_period
    percent = lunations - int(lunations)
    phase_angle = percent * 360.
    delta_t = phase_angle * lunar_period / 360.
    moon_day = int(delta_t + 0.5)
    phase = get_phase_description(phase_angle)

    return {
        'angle': phase_angle, 
        'day': moon_day, 
        'phase': phase, 
        'days_since_new_moon': delta_t
    }

def get_moon(utdt, utdt_end=None, location=None, sun=None, eph=None, apparent=False):
    """
    Create the observation dictionary for the Moon at a given UTDT.

    Sending sun and eph is just there as a way to slightly minimize work.

    TODO: Should we DEFAULT to apparent coordinates?
    """
    ts = load.timescale()
    t = ts.utc(utdt.year, utdt.month, utdt.day, utdt.hour, utdt.minute)

    if not eph:
        eph = load('de421.bsp')
    earth = eph['Earth']

    # Get Moon position
    moon = earth.at(t).observe(eph['Moon'])
    (xmlat, xmlon, xmdist) = moon.ecliptic_latlon()
    moon_lat = xmlat.radians
    moon_lon = xmlon.radians
    (moon_ra, moon_dec, moon_dist) = moon.radec()
    ra = moon_ra.hours.item()
    dec = moon_dec.degrees.item()
    constellation = get_constellation(ra, dec)
    almanac = get_object_rise_set(utdt, eph, eph['Moon'], location=location) if location else None
    # creates session
    session = get_observing_situation(ra, dec, utdt, utdt_end, location) if utdt_end and location else None

    # Get Sun position
    if not sun:
        sun = earth.at(t).observe(eph['Sun'])
    else:
        sun = sun['target']

    # Lunar Phase description
    phase = simple_lunar_phase(get_julian_date(utdt))

    # i = phase angle
    i = get_phase_angle(eph, 'moon', t).degrees.item() # degrees

    elongation = get_elongation(moon, sun)
    #x_plotting_phase_angle = get_plotting_phase_angle('Moon', i, elongation)
    # Use something different for the Moon than for inferior planets.
    plotting_phase_angle = phase['angle']

    # k = illuminated fraction of the Moon's disk
    k = fraction_illuminated(eph, 'moon', t).item() # float

    # chi = position angle of the moon's bright limb
    chi = moon_phase(eph, t).degrees.item() # degrees

    # magnitude
    """
    Empirically, I get 
        x = log10(k)
        m = -1.146_606*x**2 -5.760_663*x -11.983_484
    """
    x = math.log10(k)
    mag = -1.1466_606*x**2 - 5.760_663*x - 11.983_484

    # angular size
    # TODO: THIS GIVES THE WRONG ANSWER
    ang_size = get_angular_size(3474.8, xmdist.km, units='degrees') # diameter in degrees for the Moon

    return {
        'name': 'Moon',
        'target': moon,
        'coords': observe_to_values(moon),
        'observe': {
            'constellation': constellation,
            'illum_fraction': k * 100.,  # percent
            'apparent_mag': mag,
            'angular_diameter': ang_size,
            'angular_diameter_str': to_sex(ang_size, format='degrees'),
            'phase_angle': i,
            'phase': phase,
            'plotting_phase_angle': plotting_phase_angle,
            'position_angle': chi,
            'elongation': elongation
        },
        'almanac': almanac,
        'session': session
    }

