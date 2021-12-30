import math
from .nutation import get_obliquity

def sun_long_lat(t, apparent=False, return_dict=False, debug=False):

    # Geometric Mean Longitude
    l0 = (280.46645 + 36000.76983 * t + 3.032e-4 * t**2) % 360.
    # Mean anomaly
    m = math.radians((357.52910 + 35999.05030 * t - 1.559e-4 * t**2 - 4.8e-7 * t**3) % 360.)
    # Eccentricity of the Earth's orbit
    e = 0.016_708_817 - 4.2037e-5 * t - 1.236e-7 * t**2

    # Equation of Center
    c = (1.914600 - 0.004817 * t - 1.4e-5*t**2) * math.sin(m) \
        + (0.019993 - 1.01e-4 * t) * math.sin(2.*m) \
        + 2.9e-4 * math.sin(3.*m) # degrees

    # True longitude
    sun0 = l0 + c
    # True anomaly
    nu = math.degrees(m) + c

    # Radius vector
    r = (1 - e**2) * (1. + 1.018e-6) / (1. + e * math.cos(math.radians(nu))) # AU

    # Correct for apparent longitude
    if apparent:
        omega = math.radians((125.04 - 1934.136 * t) % 360.)
        longitude = sun0 - 0.00569 - 0.00478 * math.sin(omega)
    else:
        longitude = sun0

    if debug:
        print ("L0: ", l0)
        print ("M: ", math.degrees(m))
        print ("E: ", e)
        print ("C: ", c)
        print ("Sun: ", sun0)
        print ("Nu: ", nu)
        print ("R: ", r)
        if apparent:
            print ("Omega: ", math.degrees(omega))
            print ('Longitude: ', longitude)

    if return_dict:
        return {'longitude': longitude, 'latitude': 0., 'distance': r}
    return (longitude, 0., r)

def sun_equatorial_coords(t, return_dict=False, debug=False):
    sun, beta, r = sun_long_lat(t, apparent=True)
    xeps = math.radians(get_obliquity(t))
    xlon = math.radians(sun)
    ra = (math.degrees(math.atan2(math.cos(xeps) * math.sin(xlon), math.cos(xlon))) / 15.) % 24.
    dec = math.degrees(math.asin(math.sin(xeps) * math.sin(xlon)))

    if return_dict:
        return {'ra': ra, 'dec': dec, 'distance': r}
    return ra, dec, r

