import datetime as dt
import math
from .nutation import get_nutation, get_obliquity

TIME_ZONE_OFFSET = {
    'US/Eastern': 5,
    'US/Central': 6,
    'US/Mountain': 7,
    'US/Pacific': 8
}

SEX_FORMAT = {
    'hours': "{}{:02d}h {:02d}m {:06.3f}s",
    'hms': "{}{:02d}:{:02d}:{:02d}",
    "hmsf": "{}{:02d}:{:02d}:{:06.3f}",
    'degrees': "{:1s}{:3d}° {:02d}\' {:06.3f}\"", # SHOULD be -360 to 360
    'deg_text': "{:1s}{:3d}d {:02d}m {:06.3f}s",
    "ra": "{}{:02d}h{:02d}m{:06.3f}s", # ra SHOULD be positive, < 24
    "dec": "{:1s}{:02d}°{:02d}\'{:06.3f}\"" # dec SHOULD be -90 to 90.
}

def to_sex(value, format='hours'):
    x = abs(value)
    if format in ["hours", "hms", "hmsf", "ra"]:
        sign = '' if value > 0 else '-'
    else:
        sign = '+' if value > 0 else '-'
    h = int(x)
    x -= h
    x *= 60.
    m = int(x)
    s = (x-m) * 60
    if format == 'hms':
        s = int(s)

    return SEX_FORMAT[format].format(sign, h, m, s)

def get_ut(datetime=None, date=None, local_time=None, time_zone='US/Eastern', dst=False):
    if not datetime and date and local_time:
        datetime = dt.datetime.combine(date, local_time)
    tzo = TIME_ZONE_OFFSET.get(time_zone, 0)
    ut = datetime + dt.timedelta(hours=tzo)
    if dst:
        ut += dt.timedelta(hours=-1)
    return ut

def get_julian_date(xdt, zero=False): # takes a datetime object
    """
    Calcuate JD for a Gregorian datetime UT.
    """
    if xdt.month <= 2:
        m = xdt.month + 12
        y = xdt.year - 1
    else:
        m = xdt.month
        y = xdt.year
    a = int(y/100.)
    b = 2 - a + int(a/4.)
    jd0 = int(365.25 * (y + 4716)) \
        + int(30.6001 * (m + 1)) \
        + xdt.day + b - 1524.5
    jdut = 0.
    if not zero:
        jdut = (xdt.hour + xdt.minute / 60. + (xdt.second + (xdt.microsecond / 1.e6)) / 3600.) / 24.
    return jd0 + jdut

def get_delta_t(utdt):
    """
    Approximate ∆t

    Good for years between 2005 and 2050.
    https://eclipse.gsfc.nasa.gov/SEhelp/deltatpoly2004.html

    measured in seconds.
    """
    t = utdt.year - 2000
    if t < 5 or t > 50:
        print(u"∆T calculation error!  Year not between 2005 and 2050 - defaulting to 62.92s")
        return 62.92
    delta_t = 62.92 + 0.32217 * t + 0.005589 * t * t
    return delta_t

def get_t_epoch(jd):
    t = (jd - 2451545.0) / 36525.
    return t

def get_gmst0(utdt, format='hours'):
    x = utdt.replace(hour=0, minute=0, second=0, microsecond=0)
    jd0 = get_julian_date(x)
    t = get_t_epoch(jd0)
    #gmst = ((24110.54841 + 8_640_184.81266 * t + 9.3104e-2 * t*t - 6.2e-6 *t*t*t) / 3600.) % 24.
    gmst = (100.460_618_37 + 36_000.770_053_608 * t + 3.87933e-4 * t**2 - t**3 / 38_710_000.) % 360.
    if format == 'hours':
        gmst = gmst / 15.
    return gmst

def get_gmst(utdt):
    """
    Get the mean sidereal time at Greenwich at a UT
    """
    gst0 = get_gmst0(utdt)
    ut = utdt.hour + utdt.minute / 60 + (utdt.second + utdt.microsecond/1.e6) / 3600.
    dut = ut * 1.00273790935
    gmst = (gst0 + dut) % 24.
    return gmst

def get_gast(utdt, debug=False):
    """
    Get the apparent sidereal time at Greenwich at a UT
    """
    # Get time things
    jd = get_julian_date(utdt)
    t = get_t_epoch(jd)
    # Get Obliquity, and Nutations
    eps0 = get_obliquity(t)
    dpsi, deps = get_nutation(t) # both in arcseconds
    # Correct obliquity
    eps = eps0 + deps/3600.

    # Get GMST @ 0h
    theta0 = get_gmst(utdt)
    dtheta = dpsi * math.cos(math.radians(eps)) / 15. / 3600. # in hours
    gast = theta0 + dtheta

    if debug:
        print('dpsi: ', dpsi, ' deps: ', deps, ' eps0: ', eps0, ' eps: ', eps)
        print("THETA0: ", to_sex(theta0), " ∆:", dtheta*3600., ' GAST:', to_sex(gast))
    return gast

def get_lmst(utdt, longitude):
    """
    Local Mean Sidereal Time (LMST)
    """
    gmst = get_gmst(utdt)
    lmst = gmst + longitude/15. # degrees to hours
    lmst %= 24.
    return lmst

def get_last(utdt, longitude):
    """ 
    Local Apparent Sidereal Time (LAST)
    """
    gast = get_gast(utdt)
    last = gast + longitude/15.
    last %= 24.
    return last


