import math
from ..observe.time import get_last
from .format import to_sex

def get_alt_az(utdt, latitude, longitude, ra, dec, from_south=False, debug=False):
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