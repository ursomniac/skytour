import math
from skyfield.api import load
from skyfield.constants import GM_SUN_Pitjeva_2005_km3_s2 as GM_SUN
from skyfield.data import mpc

def get_comet_object(comet):
    with load.open('CometEls.txt') as f:
        comets = mpc.load_comets_dataframe(f)
    comets = (comets.sort_values('reference').groupby('designation', as_index=False).last().set_index('designation', drop=False))
    try:
        row = comets.loc[comet.name]
    except:
        row = None
    return row

def get_comet_target(comet, ts, sun):
    target = None
    row = get_comet_object(comet)
    if row is not None:
        target = sun + mpc.comet_orbit(row, ts, GM_SUN)
    return target, row

def get_comet_magnitude(mg, mk, r_earth_target, r_sun_target, offset=0.):
    mag = (
        mg 
        + 5. * math.log10(r_earth_target) 
        + mk * math.log10(r_sun_target)
        + offset
    )
    return mag

def get_comet_period(obj):
    p = obj['perihelion_distance_au']
    e = obj['eccentricity']
    if e >= 1.:
        return None
    a = p / (1. - e)
    period = math.sqrt(a ** 3.)
    return period



