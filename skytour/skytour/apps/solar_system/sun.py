from skyfield.api import load
from ..observe.almanac import get_object_rise_set
from .serializer import serialize_astrometric

def get_sun(utdt, location=None, eph=None):
    """
    Get the observation dict for the Sun at a given UTDT.
    If location is given, return Rise/Set information as well.
    """
    ts = load.timescale()
    t = ts.utc(utdt.year, utdt.month, utdt.day, utdt.hour, utdt.minute)
    if not eph:
        eph = load('de421.bsp')
    earth = eph['Earth']
    sun = eph['Sun']
    
    almanac = None
    if location:
        almanac = get_object_rise_set(utdt, eph, sun, location)
    target = earth.at(t).observe(sun)

    return {
        'target': earth.at(t).observe(sun),
        'apparent': serialize_astrometric(target.apparent()),
        'almanac': almanac
    }
