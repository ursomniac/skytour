from skyfield.api import load

def get_earth(utdt):
    ts = load.timescale()
    t = ts.utc(utdt.year, utdt.month, utdt.day, utdt.hour, utdt.minute)
    eph = load('de421.bsp')
    sun = eph['Sun']

    # Get the coordinates at time t from Earth
    obs = sun.at(t).observe(eph['Earth'])
    return obs
