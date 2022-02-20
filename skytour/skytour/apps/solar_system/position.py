from skyfield.api import load
from ..observe.almanac import get_object_rise_set
from ..solar_system.comets import get_comet_target, get_comet_obs
from .models import Planet, Comet
from .serializer import serialize_astrometric

def get_position(utdt, body, location=None, comet=False):
    """
    Get the serialized metadata for an object at a given utdt and location.
    """
    ts = load.timescale()
    t = ts.utc(utdt.year, utdt.month, utdt.day, utdt.hour, utdt.minute)
    eph = load('de421.bsp')
    earth = eph['Earth']
    sun = eph['Sun']
    if comet:
        eph_body, row = get_comet_target(body, ts, sun)
    else: 
        eph_body = eph[body]

    target = earth.at(t).observe(eph_body).apparent() # for solar system objects
    apparent = serialize_astrometric(target)
    almanac = get_object_rise_set(utdt, eph, eph_body, location, serialize=True) if location else None

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
        d['slug'] = p.slug
        planet_dict[p.name] = d
        # Deal with moons!
    return planet_dict

def get_comet_positions(utdt, location=None):
    comets = Comet.objects.filter(status=1)
    comet_list = []
    for c in comets:
        d = get_position(utdt, c, location=location, comet=True)
        d['pk'] = c.pk
        d['name'] = c.name
        comet_list.append(d)
    return comet_list
