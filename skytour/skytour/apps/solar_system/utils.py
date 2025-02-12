import math
from skyfield.api import (
    position_of_radec, 
    load_constellation_map,
    load_constellation_names
)

def rectify_float(delta, unit='AU'):
    d = {
        'n': (-9, 1.e9), 'µ': (-6, 1.e6), 'm': (-3, 1000.),
        '_': (0, 1.), 'k': (3, 0.001), 'M': (6, 1.e-6), 
        'G': (9, 1.e-9)
    }
    units = {-3: 'n', -2: 'µ', -1: 'm', 0: '', 1: 'k', 2: 'M', 3: 'G'}

    sign = 1.0 if delta >= 0. else -1.0
    adelta = abs(delta)
    order = math.log10(adelta)
    index = order // 3
    if index in units.keys():
        u = units[index]
        e = 10. ** (index * 3)
        f = sign * adelta / e
        return f"{f:.3f} {u}{unit}"
    else:
        return f"{delta:.3e} {unit}"


def get_angular_size(diameter, distance, units='arcsec'):  # text name, e.g., 'Mars'
    """
    Skinny triangle formula.  Diameter/Distance.
    """
    if diameter is None or distance is None:
        return None
    theta = math.degrees(math.asin(diameter/distance)) * 3600. # arcsec
    if units == 'arcmin':
        return theta / 60.
    if units == 'degrees':
        return theta / 3600.
    return theta

def get_angular_size_string(degrees):
    x = degrees
    if x is None:
        return None
    if x < 1./3600.:
        mas = x * 3.600e6 # milliarcseconds
        return f'{mas:.1f} mas'
    x_deg = int(x)
    x = (x - x_deg) * 60.
    x_min = int(x)
    x = (x - x_min) * 60.
    x_sec = x

    s = ''
    if x_deg > 0:
        s += f'{x_deg}° '
    if x_min > 0 or x_deg > 0:
        s += f'{x_min:02d}\' '

    if x_sec > 0 or x_deg > 0 or x_min > 0:
        s += f'{x_sec:05.2f}\"'
    if x_sec > 0 and x_deg == 0 and x_min == 0:
        s = f'{x_sec:5.2f}\"'

    return s

PHASES = [
    'NEW', 'WAXING CRESCENT', 'FIRST QUARTER', 'WAXING GIBBOUS', 'FULL', 
    'WANING GIBBOUS', 'LAST QUARTER', 'WANING CRESCENT', 'NEW'
]
def get_phase_description(phase_angle): # degrees
    phase = PHASES[int((phase_angle + 22.5) / 45.)]
    return phase

def get_plotting_phase_angle(name, phase, elongation):
    """
    This disambiguates elogattion making it from 0 - 360 degrees.
    """
    if name in ['Mercury', 'Venus']:
        return 360. - phase if elongation < 0. else phase
    return phase

def get_elongation(l_target, l_sun):
    """
    I think this handles E/W elongations.
    ??? if < 0. it's to the W of the Sun, E if > 0.
    """
    elongation = l_target - l_sun
    if elongation < -180.:
        elongation += 360.
    if elongation > 180.:
        elongation -= 360.
    return elongation

def get_constellation(ra, dec):
    """
    Return the constellation at a given ra, dec.
    TODO: I'm not sure if the call to Skyfield handles the precession
    from the 1875 epoch (where the constellation boundaries were 
    established) to the present-era RA/DEC.
    """
    constellation_at = load_constellation_map()
    d = dict(load_constellation_names())
    abbr = constellation_at(position_of_radec(ra, dec))
    # Stupid hack - error in Skyfield - apparently this is fixed in V1.49
    #abbr = 'Cvn' if abbr == 'CVn' else abbr
    #abbr = 'Tra' if abbr == 'TrA' else abbr
    return dict(name = d[abbr], abbr = abbr)

def get_meeus_phase_angle(sun_earth, earth_obj, sun_obj):
    c1 = sun_obj**2 + earth_obj**2 - sun_earth**2
    c2 = 2. * sun_obj * earth_obj
    cos_i = c1 / c2
    if abs(cos_i) > 1.0:
        return None
    return math.degrees(math.acos(cos_i))

def get_relation_to_planet(delta, angsep, diam):
    if delta < 0.: # in front of
        t =  ('Transit', 'T') if angsep < diam/2. else ('Front', 'F')
    else:
        t = ('Occulted', 'O') if angsep < diam/2. else ('Behind', 'B')
    #print(f'DEL: {delta} SEP: {angsep}, DIAM: {diam} T: {t}')
    return t

def get_asteroid_from_cookie(cookie, object):
    for a in cookie['asteroids']:
        if a['name'] == object.full_name:
            return a
    return None

def get_comet_from_cookie(cookie, object):
    for c in cookie['comets']:
        if c['pk'] == object.pk:
            return c
    return None

def get_planet_from_cookie(cookie, object):
    planet_cookies = cookie['planets']
    for k in planet_cookies.keys():
        if planet_cookies[k]['slug'] == object.slug:
            return planet_cookies[k]
    return None

def get_position_from_cookie(cookie):
    try:
        x = cookie['apparent']['equ']
        return x['ra'], x['dec']
    except:
        return None, None