import math
from .time import get_last
from ..utils.format import to_sex

def get_alt_az(utdt, latitude, longitude, ra, dec, from_south=False, debug=False):
    """
    Return Altitude and Azimuth.

    Returns either measured from the South, or from the North (like a compass heading)
    """
    last = get_last(utdt, longitude)
    xha = math.radians((last - ra) * 15.)
    xlat = math.radians(latitude)
    xdec = math.radians(dec)
    denom = math.cos(xha) * math.sin(xlat) - math.tan(xdec) * math.cos(xlat)
    azimuth = math.degrees(math.atan2(math.sin(xha), denom)) % 360.
    alt1 = math.sin(xlat) * math.sin(xdec)
    alt2 = math.cos(xlat) * math.cos(xdec) * math.cos(xha)
    altitude = math.degrees(math.asin(alt1 + alt2))

    if debug:
        print("XHA: ", math.degrees(xha))
        print("XDEC: ", to_sex(math.degrees(xdec), format="degrees"))
        print ("AZ: ", azimuth)
        print("ALT: ", altitude)

    if not from_south: # measure from north - default
        azimuth += 180.
        azimuth %= 360.
        
    return azimuth, altitude

def get_cartesian(longitude_or_ra, latitude_or_dec, ra_dec=True, radius=180.):
    """
    Default "unit" radius is 180 degrees
    """
    lat = math.radians(latitude_or_dec)
    lon = math.radians(longitude_or_ra)
    lon *= 15. if ra_dec else 1. # convert from hours if needed
    # normally you'd use the radius of a sphere, e.g., Earth = 6371 km,
    # but here we only care about angular distance, so use a unit sphere.
    x = radius * math.cos(lat) * math.cos(lon)
    y = radius * math.cos(lat) * math.sin(lon)
    z = radius * math.sin(lat)
    return (x, y, z)