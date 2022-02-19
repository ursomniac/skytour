from skyfield.api import load
from ..observe.almanac import get_object_rise_set
from .models import Planet
from .serializer import serialize_astrometric

def get_position(utdt, body, location=None):
    """
    Get the serialized metadata for an object at a given utdt and location.
    """
    ts = load.timescale()
    t = ts.utc(utdt.year, utdt.month, utdt.day, utdt.hour, utdt.minute)
    eph = load('de421.bsp')
    earth = eph['Earth']
    eph_body = eph[body]
    target = earth.at(t).observe(eph_body).apparent() # for solar system objects
    almanac = get_object_rise_set(utdt, eph, eph_body, location, serialize=True) if location else None
    apparent = serialize_astrometric(target)
    return dict(
        apparent = apparent,
        almanac = almanac
    )

def get_planet_positions(utdt, location=None):
    """
    This replaces the get_planet_dict (eventually)
    """
    planets = Planet.objects.order_by('pk')
    planet_dict = {}
    for p in planets:
        d = get_position(utdt, p.target, location=location)
        planet_dict[p.name] = d
        # Deal with moons!
    return planet_dict
