import datetime, pytz
from skyfield.api import load 
from .vocabs import PLANETS_8
from ..site_parameter.helpers import get_ephemeris

def get_ecliptic_positions(utdt=None):
    if utdt is None:
        utdt = datetime.datetime.now(datetime.timezone.utc)
    all_planets = PLANETS_8
    # start
    ts = load.timescale()
    t = ts.utc(utdt.year, utdt.month, utdt.day, utdt.hour, utdt.minute)
    eph = load(get_ephemeris())
    sun = eph['sun']
    points = []
    for planet in all_planets:
        loc = planet.upper() + ' BARYCENTER'
        coords = sun.at(t).observe(eph[loc])
        latitude, longitude, distance = coords.ecliptic_latlon()
        d = dict(
            name=planet,
            longitude=longitude.degrees.item(),
            latitude=latitude.degrees.item(),
            distance=distance.au.item()
        )
        points.append(d)
    return points

def get_mean_orbital_elements(name):
    ELEMENTS = {
        'Mercury': (0.38709893, 0.20563069, 7.00487, 48.33167, 77.45645, 252.25084),
        'Venus': (0.72333199, 0.00677323, 3.39471, 76.68069, 131.53298, 181.97973),
        'Earth': (1.00000011, 0.01671022, 0.00005, -11.26064, 102.94719, 100.46435),
        'Mars':	(1.52366231, 0.09341233, 1.85061, 49.57854, 336.04084, 355.45332),
        'Jupiter': (5.20336301, 0.04839266, 1.30530, 100.55615, 14.75385, 34.40438),
        'Saturn': (9.53707032, 0.05415060, 2.48446, 113.71504, 92.43194, 49.94432),
        'Uranus': (19.19126393, 0.04716771, 0.76986, 74.22988, 170.96424, 313.23218),
        'Neptune': (30.06896348, 0.00858587, 1.76917, 131.72169, 44.97135, 304.88003),
    }
    if name in ELEMENTS.keys():
        e = ELEMENTS[name]
        d = dict(
            semimajor_axis = e[0],
            eccentricity = e[1],
            inclination = e[2],
            longitude_ascending_node = e[3],
            longitude_of_perihelion = e[4],
            mean_longitude = e[5]
        )
        return d
    return None
    
