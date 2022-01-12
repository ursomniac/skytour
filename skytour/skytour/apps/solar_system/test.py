import datetime, pytz
from skyfield.almanac import phase_angle as get_phase_angle
from skyfield.api import load
from skyfield.constants import GM_SUN_Pitjeva_2005_km3_s2 as GM_SUN

from skyfield.data import mpc
from .models import Asteroid

def test_asteroid(utdt, asteroid):

    ts = load.timescale()
    eph = load('de421.bsp')
    sun, earth = eph['sun'], eph['earth']
    t = ts.utc(utdt.year, month=utdt.month, day=utdt.day, hour=utdt.hour, minute=utdt.minute, second=utdt.second)
    with load.open('bright_asteroids.txt') as f:
        mps = mpc.load_mpcorb_dataframe(f)
    mps = mps.set_index('designation', drop=False)
    row = mps.loc[asteroid.mpc_lookup_designation]
    target = sun + mpc.mpcorb_orbit(row, ts, GM_SUN)
    observe = earth.at(t).observe(target)
    #phase_angle = get_phase_angle(eph, asteroid.mpc_lookup_designation, t)
    return observe#, phase_angle

