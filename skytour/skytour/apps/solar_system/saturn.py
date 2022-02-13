import math

def saturn_ring(t, saturn, return_dict=True):
    """
    Given the obs object for Saturn, get ring information.
    """
    # Saturn's position (provided)
    geo_lat, geo_lon, geo_dist = saturn.ecliptic_latlon()
    lamb = math.radians(geo_lon.degrees.item())
    beta = math.radians(geo_lat.degrees.item())

    # inclination of the plane of the ring
    iota = math.radians(28.075_216 - 0.012_998*t + 4.e-6*t**2)
    # longitude of the ascending node
    omega = math.radians(169.508_470 + 1.394_681*t + 4.12e-4*t**2)
    
    bb = math.asin(
        math.sin(iota) * math.cos(beta) * math.sin(lamb - omega) \
            - math.cos(iota) * math.sin(beta)
    )
    # Major and minor axes of the rings in arcseconds
    a = 375.35 / geo_dist.au # geo_dist in AU;  arcsec
    b = a * math.sin(abs(bb))
    # inner ring  a, b * 0.665
    # outer ring  a, b * ?
    
    # TODO: factor in the tilt of the axis projected to the earth
    # Longitude of the ascending node of Saturn's orbit
    # n = 113.6655 + 0.8771 * t  # degrees

    return {
        'major': a,
        'minor': b,
        'i': math.degrees(iota),
        'b': math.degrees(bb)
    }