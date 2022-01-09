import datetime
import math
from skyfield.api import load
from ..observe.astro import get_obliquity
from ..observe.time import get_julian_date, estimate_delta_t
from .earth import get_earth
from .models import Planet

def _cosd(d):
    return math.cos(math.radians(d))
def _sind(d):
    return math.sin(math.radians(d))
def _tand(d):
    return math.tan(math.radians(d))


def get_mars_physical_ephem(utdt, debug=False):
    """
    Meeus, 2nd Ed., chapter 41
    All we need here is D_E and omega
    """
    # The planet record
    planet = Planet.objects.filter(name='Mars').first()
    if not planet:
        return None

    jd = get_julian_date(utdt)
    delta_t = estimate_delta_t(utdt)
    jde = jd + delta_t/86400.
    tt = (jde - 2_451_545) / 36525.
    eps0 = get_obliquity(tt)

    # Things from Skyfield to get things started.
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
    omega = (w - zeta) % 360.

    mars = dict(
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

def get_mars_features(utdt, mars):
    features = [
        dict(name='Olympus Mons', longitude=226, latitude=19),
        dict(name='Valles Marineris', longitude=291, latitude=-12),
        dict(name='Syrtis Major Planum', longitude=70, latitude=8)
    ]
    meridian = mars['omega'] # degrees
    fdicts = []
    for feature in features:
        fdict = feature
        ha_degrees = feature['longitude'] - meridian
        if ha_degrees < 0.:
            ha_degrees += 360.
        dtt = ha_degrees * 24.624 / 360.
        t_trans = utdt - datetime.timedelta(hours=dtt)  
        if dtt < 0: # still to come
            t_trans = t_trans + datetime.datetime(hours=24.624)
        view = 'No'
        if abs(dtt) < 6.156:
            view = 'Edge'
        if abs(dtt) < 2.46:
            view = 'Possible'
        if abs(dtt) < 1.23:
            view = 'Best'

        fdict['meridian'] = meridian
        fdict['ha_deg'] = ha_degrees
        fdict['view'] = view
        fdict['next_transit'] = t_trans
        fdict['time_from_meridian'] = dtt
        fdicts.append(fdict)
    return fdicts