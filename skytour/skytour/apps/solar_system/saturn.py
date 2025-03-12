import math

def saturn_ring(t, pdict):
    """
    Given the obs object for Saturn, get ring information.
    """
    # Saturn's position (provided)
    ecl_lat = pdict['apparent']['ecl']['latitude']
    ecl_lon = pdict['apparent']['ecl']['longitude']
    distance = pdict['apparent']['distance']['au']

    lamb = math.radians(ecl_lon)
    beta = math.radians(ecl_lat)

    # inclination of the plane of the ring
    iota = math.radians(28.075_216 - 0.012_998*t + 4.e-6*t**2)
    # longitude of the ascending node
    omega = math.radians(169.508_470 + 1.394_681*t + 4.12e-4*t**2)
    
    bb = math.asin(
        math.sin(iota) * math.cos(beta) * math.sin(lamb - omega) \
            - math.cos(iota) * math.sin(beta)
    )
    # Major and minor axes of the rings in arcseconds
    a = 375.35 / distance # geo_dist in AU;  arcsec
    b = a * math.sin(abs(bb))
    # inner ring  a, b * 0.665
    # outer ring  a, b * ?
    
    # TODO V2.x: factor in the tilt of the axis projected to the earth
    # Longitude of the ascending node of Saturn's orbit
    # n = 113.6655 + 0.8771 * t  # degrees

    return {
        'major': a,
        'minor': b,
        'i': math.degrees(iota),
        'b': math.degrees(bb)
    }