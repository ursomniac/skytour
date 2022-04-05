import datetime, pytz
from skyfield.api import load 
from .vocabs import PLANETS_8

def get_ecliptic_positions(utdt=None):
    if utdt is None:
        utdt = datetime.datetime.utcnow().replace(tzinfo=pytz.utc)
    all_planets = PLANETS_8
    # start
    ts = load.timescale()
    t = ts.utc(utdt.year, utdt.month, utdt.day, utdt.hour, utdt.minute)
    eph = load('de421.bsp')
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

    
