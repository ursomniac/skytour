from skyfield.api import load
from ..observe.almanac import get_object_rise_set
from .serializer import serialize_astrometric

def get_position(utdt, body, location=None):
    """
    Get the serialized metadata for an object at a given utdt and location.
    """
    ts = load.timescale()
    t = ts.utc(utdt.year, utdt.month, utdt.day, utdt.hour, utdt.minute)
    eph = load['de421.bsp']
    earth = eph['Earth']
    eph_body = eph[body]
    target = earth.at(t).observe(eph_body).apparent() # for solar system objects
    almanac = get_object_rise_set(utdt, eph, eph_body, location) if location else None
    apparent = serialize_astrometric(target)
    return dict(
        apparent = apparent,
        almanac = almanac
    )
