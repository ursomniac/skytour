import math
import datetime

def has_elements(obj):
    return hasattr(obj, 'elements')

def set_t(utdt):
    utdt = utdt if utdt is not None else datetime.datetime.now(datetime.timezone.utc)
    year = utdt.year
    y0 = datetime.datetime(year + 0, 1, 1, 0, 0, 0)
    y1 = datetime.datetime(year + 1, 1, 1, 0, 0, 0)
    dy = (y1 - y0).days # handle leap years
    dd = (utdt - y0).total_seconds() / 86400.
    f = dd / dy
    return year + f

def kepler(ecc, m, debug=False, loop=10, end=1.e-10):
    """
    Method 2 by Meeus, Chapter 30
    """
    e0 = m
    ecc0 = 180. * ecc / math.pi
    err = 1.e10

    while(err > end):
        e0r = math.radians(e0)
        e1n = m + ecc0 * math.sin(e0r) - e0
        e1r = 1 - ecc * math.cos(e0r)
        e1 = e0 + (e1n / e1r)
        err = e1 - e0
        if debug:
            print(f"E0: {e0}\tΔ: {err}\tE1: {e1}")
        e0 = e1
        loop -= 1
        if loop == 0:
            break
    return e0

def binary_position(x, t, debug=False):
    t = t if t is not None else set_t(None)
    n = 360.0 / x._p
    m = n * (t - x._t)

    # get mean anomaly
    e = kepler(x._e, m)
    er = math.radians(e)
    # get radius vector
    r = x._a * (1.0 - x._e * math.cos(er))

    # get true anomaly
    tn = math.sqrt((1. + x._e)/(1. - x._e)) * math.tan(er/2.)
    nu = 2. * math.atan(tn) # radians

    # find θ - Ω, where θ is the position angle
    t1 = math.sin(nu + x._apr) * math.cos(x._ir)
    t2 = math.cos(nu + x._apr)

    thom = math.atan2(t1, t2) # radians
    theta_r = thom + x._omr
    theta = math.degrees(theta_r) % 360.  # N: 0°  E: 90°  S: 180°  W: 270°
    # separation
    x1 = math.sin(nu + x._apr)**2 * math.cos(x._ir)**2
    x2 = math.cos(nu + x._apr)**2
    rho = r * math.sqrt(x1 + x2)

    if debug:
        print(f"\tn\t{n}")
        print(f"\tt–T\t{t-x._t}")
        print(f"\tM\t{m}\t{m % 360.}")
        print(f"\tE\t{e % 360.}")
        print(f"\tr\t{r}")
        print(f"\tν\t{math.degrees(nu) % 360.}")
        print(f"\ttan(θ-Ω)\t{t1}/{t2}")
        print(f"\t(θ-Ω)\t{math.degrees(thom) % 360.}")
        print(f"\tθ\t{theta}")
        print(f"\tρ\t{rho}")

    return theta, rho


    