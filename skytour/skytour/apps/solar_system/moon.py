import math
from .utils import get_phase_description

LUNAR_PERIOD = 29.530588853

def get_moon_color(moon_day):
    angle = 0.5 * (moon_day * math.pi / (LUNAR_PERIOD / 2.)) 
    b = math.sin(angle) # between 0 and 1
    b_max = 144
    rgb = int(b*b_max)
    hex = f'#{rgb:02x}{rgb:02x}{rgb:02x}'
    return hex

def simple_lunar_phase(jd):
    """
    This just does a quick-and-dirty estimate of the Moon's phase given the date.
    """

    lunations = (jd - 2451550.1) / LUNAR_PERIOD
    percent = lunations - int(lunations)
    phase_angle = percent * 360.
    delta_t = phase_angle * LUNAR_PERIOD / 360.
    moon_day = int(delta_t + 0.5)
    phase = get_phase_description(phase_angle)
    bgcolor = get_moon_color(delta_t)
    return dict(
        angle = phase_angle, 
        day = moon_day, 
        phase = phase, 
        days_since_new_moon = delta_t,
        bgcolor = bgcolor,
    )

def equ_lunar_phase_angle(moon, sun, r_earth_sun, r_earth_moon):
    """
    Moon and Sun are the 'apparent' parts of their cookie dicts.
    """
    dec = math.radians(moon['equ']['dec'])
    dec0 = math.radians(sun['equ']['dec'])
    ra = math.radians(moon['equ']['ra']*15.)
    ra0 = math.radians(sun['equ']['ra']*15.)
    c1 = math.sin(dec0) * math.sin(dec)
    c2 = math.cos(dec0) * math.cos(dec) * math.cos(ra0 - ra)
    cos_psi = c1 + c2
    psi = math.acos(cos_psi)
    sin_psi = math.sin(psi)

    i1 = r_earth_sun * sin_psi
    i2 = r_earth_moon - r_earth_sun * cos_psi
    i = math.atan2(i1, i2) # aradian
    return math.degrees(i)


def lunar_phase_angle(beta, lam, lam0, earth_sun, earth_moon):
    """
    This gives the wrong answer?  Somehow.
    """
    cos_phi = math.cos(beta) * math.cos(lam - lam0)
    phi = math.acos(cos_phi) # radians
    t1 = earth_sun * math.sin(phi)
    t2 = earth_moon - earth_sun * cos_phi
    phase_angle = math.atan2(t1, t2)
    return math.degrees(phase_angle)