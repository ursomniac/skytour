import datetime, pytz
import math
from skyfield.api import load
from skyfield.constants import GM_SUN_Pitjeva_2005_km3_s2 as GM_SUN
from skyfield.data import mpc
from ..observe.almanac import get_object_rise_set
from ..observe.local import get_observing_situation
from ..utils.compile import observe_to_values
from .utils import get_constellation

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

def get_comet(utdt, comet, utdt_end=None, location=None):
    if utdt is None:
        utdt = datetime.datetime.utcnow().replace(tzinfo=pytz.utc)
    ts = load.timescale()
    t = ts.utc(utdt)

    eph = load('de421.bsp')
    sun, earth = eph['sun'], eph['earth']
    target, row = get_comet_target(comet, ts, sun)

    # Earth to Comet
    obs = earth.at(t).observe(target)
    xra, xdec, xdelta = obs.radec()
    delta = xdelta.au.item()
    constellation = get_constellation(xra.hours.item(), xdec.degrees.item())
    
    # Earth to Sun
    earth_sun = earth.at(t).observe(sun)
    _, _, xrr = earth_sun.radec() # get distance Earth-Sun
    rr = xrr.au.item()
    # Sun to comet
    sun_comet = sun.at(t).observe(target)
    _, _, xr = sun_comet.ecliptic_latlon() # get distance to the Sun
    r = xr.au.item()

    # Get Phase Angle
    cos_beta = (r*r + delta*delta - rr*rr) / (2. * r * delta)
    phase_angle = math.acos(cos_beta) # RADIANS
    # Get Elongation
    cos_psi = (rr*rr + delta*delta - r*r)/(2. * r * delta)
    try:
        psi = math.degrees(math.acos(cos_psi))
    except:
        print ("COS PSI ERROR: ", cos_psi)
        psi = None

    # Get apparent magnitude
    g = row['magnitude_g']
    k = row['magnitude_k']
    m = g + 5 * math.log10(delta) + k * math.log10(r)

    # If location is provided, get the almanac dict
    almanac = get_object_rise_set(utdt, eph, target, location) if location else None
    # if location AND utdt_end are provided, get the session dict
    session = get_observing_situation(obs, utdt, utdt_end, location) if utdt_end and location else None

    return dict(
        name = comet.name,
        pk = comet.pk,
        object = comet,
        target = obs,
        coords = observe_to_values(obs),
        comet = row, # This is a panads Series which acts like a dict
        observe = dict(
            constellation=constellation,
            angular_diameter = None,
            apparent_mag = m,
            phase_angle = math.degrees(phase_angle),
            elongation = psi,
        ),
        physical = None,
        close_to = None,
        moons = None,
        sun_distance = r,
        earth_sun_distance = rr,
        almanac = almanac,
        session = session
    )
    