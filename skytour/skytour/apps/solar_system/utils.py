import math

def get_angular_size(diameter, distance, units='arcsec'):  # text name, e.g., 'Mars'
    #print ("DIAMETER: ", diameter, 'DISTANCE: ', distance)
    theta = math.degrees(math.asin(diameter/distance)) * 3600. # arcsec
    if units == 'arcmin':
        return theta / 60.
    if units == 'degrees':
        return theta / 3600.
    return theta

def old_get_plotting_phase_angle(phase_angle, target, sun):
    obj_lon = target.ecliptic_latlon()[1].degrees
    sun_lon = sun.ecliptic_latlon()[1].degrees
    dl = obj_lon - sun_lon
    if dl > 180.:
        dl = dl - 360.
    plotting_phase = 360 - phase_angle if dl < 0. else phase_angle

PHASES = [
    'NEW', 'WAXING CRESCENT', 'FIRST QUARTER', 'WAXING GIBBOUS', 'FULL', 
    'WANING GIBBOUS', 'LAST QUARTER', 'WANING CRESCENT', 'NEW'
]
def get_phase_description(phase_angle): # degrees
    phase = PHASES[int((phase_angle + 22.5) / 45.)]
    return phase

def get_plotting_phase_angle(target, sun):
    _, mlon, _ = target.apparent().ecliptic_latlon('date')
    _, slon, _ = sun.apparent().ecliptic_latlon('date')
    angle = mlon.degrees - slon.degrees
    return angle