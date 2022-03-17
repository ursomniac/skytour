import datetime, pytz
import math
from skyfield.api import load
from ..apps.observe.astro import get_obliquity
from ..apps.observe.time import get_julian_date, estimate_delta_t

def _cosd(d):
    return math.cos(math.radians(d))
def _sind(d):
    return math.sin(math.radians(d))
def _tand(d):
    return math.tan(math.radians(d))


def get_mars_physical_ephem(utdt, planet, debug=False):
    """
    Meeus, 2nd Ed., chapter 41
    All we need here is D_E and omega
    """
    if debug:
        utdt = datetime.datetime(1992, 11, 9, 0, 0).replace(tzinfo=pytz.utc)
    jd = get_julian_date(utdt)
    delta_t = estimate_delta_t(utdt)
    jde = jd + delta_t/86400.
    tt = (jde - 2_451_545) / 36525.
    eps0 = (23. + 26/60. + 21.448/3600.) - (46.8150*tt + 5.9e-4 * tt**2 + 1.813 * tt**3)/3600.

    if debug:
        print("JD: ", jd)
        print("∆T: ", delta_t)
        print("JDE: ", jde)
        print("TT: ", tt)
        print("Eps0: ", eps0)

    # Things from Skyfield to get things started.
    if not debug:
        ts = load.timescale()
        t = ts.utc(utdt.year, utdt.month, utdt.day, utdt.hour, utdt.minute)
        eph = load('de421.bsp')
        earth = eph['earth']
        sun = eph['sun']
        mars = eph[planet.target]
    
    # Get the heliocentric coordinates of the Earth
        sun_earth = sun.at(t).observe(earth)
        xb0, xl0, xr0 = sun_earth.ecliptic_latlon()

        b0 = xb0.degrees.item()
        l0 = xl0.degrees.item()
        r0 = xr0.au.item()
    else:
        b0 = -0.000167
        l0 = 46.843_861
        r0 = 0.990_413_01

    # Get the coordinates at time t from Earth
    if not debug:
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
    else:
        b = 0.896_321
        l = 78.473_759
        r = 1.541_659_4

        

    
    # get x, y, z
    x = r * _cosd(b) * _cosd(l) - r0 * _cosd(l0)
    y = r * _cosd(b) * _sind(l) - r0 * _sind(l0)
    z = r * _sind(b)            - r0 * _sind(b0)

    if debug:
        delta0 = math.sqrt(x**2 + y**2 + z**2)
        tau = delta0 * 149_597_870.691 / 299792.458 / 86400.
        print("TAU: ", tau)
        print("\nX: ", x)
        print("Y: ", y)
        print("Z: ", z)
        print("∆: ", math.sqrt(x**2 + y**2 + z**2))

    # Mars geocentric longitude and latitude
    lam = math.degrees(math.atan2(y, x)) # degrees
    beta = math.degrees(math.atan2(z, math.sqrt(x*x + y*y)))

    if debug:
        print("Lam:  ", lam)
        print("Beta: ", beta)
    
    # Mars north pole position
    lam0 = 352.9065 + 1.17330 * tt # degrees
    bet0 =  63.2818 + 0.00394 * tt # degrees

    # D_E
    d_e = math.degrees(math.asin(
        -1. * _sind(bet0) * _sind(beta) 
        - _cosd(bet0) * _cosd(beta) * _cosd(lam0 - lam)
    ))

    if debug:
        print ("D_E: ", d_e)

    # Get W
    wt = jde - tau - 2_433_282.5
    w = (11.504 + 350.892_000_25 * wt) % 360.

    if debug:
        print ("\nW: ", w)

    # Get equatorial coordiantes of the pole
    rp1 = _sind(lam0) * _cosd(eps0) - _tand(bet0) * _sind(eps0)
    rp2 = _cosd(lam0)
    ra_pole = math.degrees(math.atan2(rp1, rp2)) % 360. # degrees
    dec_pole = math.degrees(math.asin(
        _sind(bet0) * _cosd(eps0) + _cosd(bet0) * _sind(eps0) * _sind(lam0)
    )) # degrees

    if debug:
        print ("RA Pole: ", ra_pole)
        print ("Dec. Pole: ", dec_pole)

    u = y * _cosd(eps0) - z * _sind(eps0)
    v = y * _sind(eps0) + z * _cosd(eps0)

    if debug:
        print ("u: ", u)
        print ("v: ", v)

    alpha = math.degrees(math.atan2(u, x)) # degrees
    delta = math.degrees(math.atan2(v, math.sqrt(x*x + u*u))) # degrees

    if debug:
        print("alpha: ", alpha)
        print("delta: ", delta)
        

    zeta1a = _sind(dec_pole) * _cosd(delta) * _cosd(ra_pole - alpha)
    zeta1b = _sind(delta) * _cosd(dec_pole)
    zeta1 = zeta1a - zeta1b
    zeta2 = _cosd(delta) * _sind(ra_pole - alpha)
    zeta = math.degrees(math.atan2(zeta1, zeta2)) % 360.

    if debug:
        print("zeta: ", zeta)

    # FINALLY, longitude of central meridian
    # The offset is to align with the map
    omega = (w - zeta) % 360.

    if debug:
        print ("omega: ", omega)

    mars = dict(
        omega=omega,
        zeta=zeta,
        d_e=d_e
    )
    #mars['features'] = get_mars_features(utdt, mars)

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
