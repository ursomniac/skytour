from skyfield.api import load
from ..observe.almanac import get_object_rise_set

def get_sun(utdt, location=None, eph=None):
    ts = load.timescale()
    t = ts.utc(utdt.year, utdt.month, utdt.day, utdt.hour, utdt.minute)
    if not eph:
        eph = load('de421.bsp')
    earth = eph['Earth']
    sun = eph['Sun']
    
    almanac = None
    if location:
        almanac = get_object_rise_set(utdt, eph, sun, location)
    
    return {
        'target': earth.at(t).observe(sun),
        'almanac': almanac
    }
