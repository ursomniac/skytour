
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
