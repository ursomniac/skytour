import math
from skyfield.api import (
    position_of_radec, 
    load_constellation_map,
    load_constellation_names
)

def get_angular_size(diameter, distance, units='arcsec'):  # text name, e.g., 'Mars'
    """
    Skinny triangle formula.  Diameter/Distance.
    """
    #print ("DIAMETER: ", diameter, 'DISTANCE: ', distance)
    theta = math.degrees(math.asin(diameter/distance)) * 3600. # arcsec
    if units == 'arcmin':
        return theta / 60.
    if units == 'degrees':
        return theta / 3600.
    return theta

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

def get_elongation(target, sun):
    """
    This doesn't disambiguate between eastern and western elongations.
    """
    _, mlon, tdist = target.apparent().ecliptic_latlon('date')
    _, slon, sdist = sun.apparent().ecliptic_latlon('date')
    angle = mlon.degrees - slon.degrees
    return angle

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
    return dict(name = d[abbr], abbr = abbr)