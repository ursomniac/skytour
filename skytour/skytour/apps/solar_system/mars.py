import datetime
import math
from skyfield.api import load
from ..astro.altaz import get_obliquity
from ..astro.time import get_julian_date, estimate_delta_t
from ..site_parameter.helpers import get_ephemeris
from .vocabs import MARS_FEATURES

# Trig functions for degrees
def _cosd(d):
    return math.cos(math.radians(d))
def _sind(d):
    return math.sin(math.radians(d))
def _tand(d):
    return math.tan(math.radians(d))


def get_mars_physical_ephem(utdt, planet, fudge=0, debug=False):
    """
    Meeus, 2nd Ed., chapter 41
    All we need here is D_E and omega

    For some reason the #'s in Stellarium and these calcuations are different.
    I THINK it might be because the central meridian definition for Mars is different in Meeus???
    So, fudge is applied to omega to line things up.
    58.01676611111111
    """
    jd = get_julian_date(utdt)
    delta_t = estimate_delta_t(utdt)
    jde = jd + delta_t/86400.
    tt = (jde - 2_451_545) / 36525.
    #eps0 = get_obliquity(tt)
    eps0 = (23. + 26/60. + 21.448/3600.) - (46.8150*tt + 5.9e-4 * tt**2 + 1.813 * tt**3)/3600.

    # Things from Skyfield to get things started.
    ts = load.timescale()
    t = ts.utc(utdt.year, utdt.month, utdt.day, utdt.hour, utdt.minute)
    eph = load(get_ephemeris())
    earth = eph['earth']
    sun = eph['sun']
    mars = eph[planet.target]
    
    # Get the heliocentric coordinates of the Earth
    sun_earth = sun.at(t).observe(earth)
    xb0, xl0, xr0 = sun_earth.ecliptic_latlon()
    b0 = xb0.degrees.item()
    l0 = xl0.degrees.item()
    r0 = xr0.au.item()
    # Get the coordinates at time t from Earth
    earth_mars = earth.at(t).observe(mars)
    #bem, lem, dem = earth_mars.ecliptic_latlon()
    # Get Heliocentric coordinates of Mars
    # BUT for time utdt - tau where tau is the light-time distance to the earth
    tau = earth_mars.light_time # days
    dut = utdt - datetime.timedelta(days=tau)
    t2 = ts.utc(dut.year, dut.month, dut.day, dut.hour, dut.minute)
    sun_mars = sun.at(t2).observe(mars)
    xb, xl, xr = sun_mars.ecliptic_latlon()
    b = xb.degrees.item()
    l = xl.degrees.item()
    r = xr.au.item()
    
    # get x, y, z
    x = r * _cosd(b) * _cosd(l) - r0 * _cosd(l0)
    y = r * _cosd(b) * _sind(l) - r0 * _sind(l0)
    z = r * _sind(b)            - r0 * _sind(b0)

    # Mars geocentric longitude and latitude
    lam = math.degrees(math.atan2(y, x)) # degrees
    beta = math.degrees(math.atan2(z, math.sqrt(x*x + y*y)))

    # Mars north pole position
    lam0 = 352.9065 + 1.17330 * tt # degrees
    bet0 =  63.2818 + 0.00394 * tt # degrees

    # D_E
    d_e = math.degrees(math.asin(
        -1. * _sind(bet0) * _sind(beta) 
        - _cosd(bet0) * _cosd(beta) * _cosd(lam0 - lam)
    ))

    # Get W
    wt = jde - tau - 2_433_282.5
    w = (11.504 + 350.892_000_25 * wt) % 360.

    # Get equatorial coordiantes of the pole
    rp1 = _sind(lam0) * _cosd(eps0) - _tand(bet0) * _sind(eps0)
    rp2 = _cosd(lam0)
    ra_pole = math.degrees(math.atan2(rp1, rp2)) # degrees
    dec_pole = math.degrees(math.asin(
        _sind(bet0) * _cosd(eps0) + _cosd(bet0) * _sind(eps0) * _sind(lam0)
    )) # degrees
    u = y * _cosd(eps0) - z * _sind(eps0)
    v = y * _sind(eps0) + z * _cosd(eps0)
    alpha = math.degrees(math.atan2(u, x)) # degrees
    delta = math.degrees(math.atan2(v, math.sqrt(x*x + u*u))) # degrees
    zeta1a = _sind(dec_pole) * _cosd(delta) * _cosd(ra_pole - alpha)
    zeta1b = _sind(delta) * _cosd(dec_pole)
    zeta1 = zeta1a - zeta1b
    zeta2 = _cosd(delta) * _sind(ra_pole - alpha)
    zeta = math.degrees(math.atan2(zeta1, zeta2))

    # FINALLY, longitude of central meridian
    # The offset is to align with the map
    omega0 = (w - zeta) % 360.
    omega = omega0 + fudge

    mars = dict(
        omega0=omega0,
        omega=omega,
        zeta=zeta,
        d_e=d_e
    )
    mars['features'] = get_mars_features(utdt, mars)

    if debug:
        print ("JDE: ", jde, "T: ", tt)
        print ("POLE  LAM: ", lam0, 'BETA: ', bet0)
        print ("SUN EARTH  LAM: ", l0, 'BET: ', b0, 'DIST: ', r0)
        print ("SUN MARS:  LAM: ", l, 'BETA: ', b, 'DIST', r)
        print ("LIGHT TIME: ", tau)
        print ("X: ", x, "Y: ", y, "Z: ", z)
        print ("LAMBDA: ", lam, 'BETA: ', beta)
        print ("D_E: ", d_e)
        print ("W: ", w)
        print ("EPS0: ", eps0)
        print ("POLE RA: ", ra_pole, "DEC: ", dec_pole)
        print ("U: ", u, 'V: ', v)
        print ("ALPHA: ", alpha, 'DELTA: ', delta)
        print ("ZETA: ", zeta)
        print ("OMEGA: ", omega)

    return mars

MARS_DAY = 24.624
MARS_HALF_DAY = MARS_DAY / 2.

def get_mars_features(utdt, mars):
    """
    Assemble the list of Martian surface features and estimate their visiblity.
    """
    meridian = mars['omega'] # degrees
    fdicts = []
    for feature in MARS_FEATURES:
        fdict = feature
        map_longitude = 360 - fdict['longitude']
        ha_degrees = map_longitude - meridian
        if ha_degrees < 0.:
            ha_degrees += 360.
        dtt = ha_degrees * MARS_DAY / 360.
        t_trans = utdt - datetime.timedelta(hours=dtt)
        if dtt < 0: # still to come
            t_trans = t_trans + datetime.datetime(hours=24.624)
        xtd = dtt
        if xtd > MARS_HALF_DAY:
            xtd -= MARS_DAY
        if xtd < -1.*MARS_HALF_DAY:
            xtd += MARS_DAY
        view = 'No'
        if abs(xtd) < 6.156:
            view = 'Edge'
        if abs(xtd) < 2.46:
            view = 'Possible'
        if abs(xtd) < 1.23:
            view = 'Best'

        #print(f"{feature['name']}: {feature['longitude']} - {meridian} = {ha_degrees}")
        fdict['meridian'] = meridian
        fdict['ha_deg'] = ha_degrees
        fdict['view'] = view
        fdict['next_transit'] = t_trans.isoformat()
        fdict['time_from_meridian'] = dtt
        fdicts.append(fdict)
    return fdicts