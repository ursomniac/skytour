from skyfield.api import position_of_radec, load_constellation_map
from skytour.apps.stars.models import BrightStar
from skytour.apps.utils.models import Constellation

def get_constellations():
    cc = Constellation.objects.all()
    d = {}
    for c in cc:
        abbr = c.abbreviation
        d[abbr] = c
    return d

CONSTELLATIONS = get_constellations()
MAP = load_constellation_map()

def get_stars():
    bb = BrightStar.objects.all()
    return bb

def set_constellation(b):
    x = position_of_radec(b.ra, b.dec)
    c = MAP(x).upper()
    b.constellation = CONSTELLATIONS[c]
    b.save()

def go():
    stars = get_stars()
    for star in stars:
        set_constellation(star)
