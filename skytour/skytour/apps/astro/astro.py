import math
from ..observe.models import ObservingLocation
from ..site_parameter.helpers import find_site_parameter

def get_altitude(last, lat, ra, dec):
    """
    At a given local apparent sidereal time, and latitude,
    get the altitude of an object at coordinates (ra, dec).
    """
    ha = 15.*(last-ra)
    xha = math.radians(ha)
    s1 = math.sin(math.radians(lat)) * math.sin(math.radians(dec))
    s2 = math.cos(math.radians(lat)) * math.cos(math.radians(dec)) * math.cos(xha)
    return s1 + s2 # sine of the altitude

def get_delta_hour_for_altitude(dec, alt=20, dlat=None, send='days', debug=False):
    """
    Calculate range of hour angle for an object's max altitude for a given latitude and declination.
    """
    # H = theta - RA : theta is local sidereal time
    # sin h = sin phi sin dec + cos phi cos dec cos H
    # H is zero on the meridian
    rdec = math.radians(dec)
    ralt = math.radians(alt)
    # latitude
    if dlat is None:
        pk = find_site_parameter('default-location-id', default=1, param_type=int)
        loc = ObservingLocation.objects.get(pk=pk)
        dlat = loc.latitude
    if debug:
        print(f"PHI: {dlat} = {phi}")
    phi = math.radians(dlat)

    t1 = math.sin(ralt) - (math.sin(phi) * math.sin(rdec))
    t2 = math.cos(phi) * math.cos(rdec)

    cos_hh = t1 / t2
    if cos_hh < -1.0: # circumpolar
        return None, cos_hh
    if cos_hh > 1.0: # never reaches this altitude
        return None, cos_hh
    # OK this should be valid
    hh = math.acos(t1/t2)
    if send == 'radians':
        return hh, cos_hh
    ha = math.degrees(hh)
    if send == 'degrees':
        return ha, cos_hh
    hrs = ha / 15.
    if send == 'hours':
        return hrs, cos_hh
    days = ha * 365 / 360.
    return days, cos_hh
    
def solar_system_apparent_magnitude(
        earth_dist,
        sun_dist,
        h,
        phase_angle,
        g = 0.15
    ):
    """
    Return planetary apparent magnitude based on distances, G and H.
    Stellarium uses:

    d = 5.* math.log(dr)
    phase in DEGREES

    Io: -1.68 + d + phaseDeg * (0.046 - 0.0010*phaseDeg)
    Europa: -1.41 + d + phaseDeg * (0.0312 - 0.00125*phaseDeg)
    Ganymede: -2.09 + d + phaseDeg * (0.0323 - 0.00066*phaseDeg)
    Callisto: -1.05 + d + phaseDeg * (0.078 - 0.00274*phaseDeg)
    """
    m1 = h + 5 * math.log10(sun_dist * earth_dist)
    if phase_angle:
        rpa = math.radians(phase_angle) # Assuming this is the same phase angle
        phi_1 = math.exp(-3.33 * math.tan(rpa/2.)**0.63)
        phi_2 = math.exp(-1.87 * math.tan(rpa/2.)**1.22)
        m2 = 2.5 * math.log10((1 - g) * phi_1 + g * phi_2)
    else:
        m2 = -g
    mag = m1 - m2
    return mag

def galilean_magnitude(name, h, phi, d_e, d_s):
    """
    Return apparent magnitude of Galilean Satellites based on distances and phase angle.
    """
    terms = {
        'Io':        [0.046,  0.0010],
        'Europa':    [0.0312, 0.00125],
        'Ganymede':  [0.0323, 0.00066],
        'Callisto':  [0.078,  0.00274]
    }
    d = 5. * math.log10(d_e * d_s)
    mag = h + d + phi*(terms[name][0] - terms[name][1]*phi)
    return mag

