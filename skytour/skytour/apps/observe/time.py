import datetime
import math
import pytz

from ..utils.format import to_sex
from .astro import get_nutation, get_obliquity

# TODO: Change this to a model?  For just me it's not particularly necessary
# since I'm not likely to be moving around THAT much...
TIME_ZONES = (
    ('UTC', 'UTC'),
    ('US/Eastern', 'US/Eastern'),
)

#### DATETIME METHODS
def get_local_datetime(xdate, xtime, xzone):
    """
    Combine a datetime date and time to a datetime object.
    Then, apply the time_zone localization
    """
    local_time = datetime.datetime.combine(xdate, xtime)
    local_time = local_time.replace(tzinfo=pytz.timezone(xzone))
    return local_time

def get_utdt(utdt=None):
    """
    Take a non-TZ aware datetime and return an aware one.
    """
    if not utdt:
        utdt = datetime.datetime.now()
    return utdt.replace(tzinfo=pytz.utc)

def utdt_to_local_time(utdt, timezone_name='US/Eastern'):
    utdt.replace(pytz.utc) # force UTC 
    local_time = utdt.astimezone(pytz.timezone(timezone_name))
    return local_time

def local_time_to_utdt(local_time):
    return local_time.astimezone(pytz.timezone('UTC'))

def get_0h(utdt):
    return utdt.replace(hour=0, minute=0, second=0, microsecond=0)

#### Astronomy methods
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

def get_t_epoch(jd):
    """
    Get the JD in julian centuries
    """
    t = (jd - 2451545.0) / 36525.
    return t

def estimate_delta_t(utdt):
    """
    Using https://eclipse.gsfc.nasa.gov/SEcat5/deltatpoly.html
    """
    year = utdt.year + (utdt.month - 0.5) / 12.
    #   NASA polynomials
    if year >= 2150.:
        t = (year - 1820)/100.
        dt = -20 + 32 * t**2
    elif year >= 2050 and year < 2150:
        dt = -20 + 32 * ((year - 1820)/100.)**2 - 0.5628 * (2150-year)
    elif year >= 2005 and year <= 2050:
        t = (year - 2000)
        dt = 62.92 + 0.32217*t + 5.589e-3*t**2
    elif year >=1986 and year < 2005:
        t = (year - 2000)
        dt = 63.86 + 0.3345*t - 0.060374*t**2 + 1.7275e-3*t**3 + 6.51814e-4*t**4 + 2.373599e-5*t**5
    elif year >= 1961 and year < 1986:
        t = (year - 1975)
        dt = 45.45 + 1.067*t - t**2/260 - t**3/718
    elif year >= 1941 and year < 1961:
        t = (year - 1950)
        dt = 29.07 - 0.407*t - t**2/233. + t**3/2547.
    elif year >= 1920 and year < 1941:
        t = (year - 1920)
        dt = 21.20 + 0.84493*t - 0.0761*t**2 + 2.0936e-3*t**3
    elif year >= 1900 and year < 1920:
        t = (year - 1900)
        dt = -2.79 + 1.494119*t - 0.0598939*t**2 + 0.0061966*t**3 - 1.97e-4*t**4
    elif year >= 1860 and year < 1900:
        t = (year - 1860)
        dt = 7.62 + 0.5737*t - 0.251754*t**2 + 0.01680668*t**3 - 4.473624*t**4 + t**5/233174
    elif year >= 1800 and year < 1860:
        t = (year - 1800)
        dt = 13.72 - 0.332447*t + 6.8612e-3*t**2 + 4.1116e-3*t**3 - 3.7436e-4*t**4 + 1.21272e-5*t**5 \
            -1.699e-7*t**6 + 8.75e-10*t**7
    elif year >= 1700 and year < 1800:
        t = (year - 1700)
        dt = 8.83 + 0.1603*t - 5.9285e-3*t**2 + 1.3336e-4*t**3 - t**4/1_174_000
    elif year >= 1600 and year < 1700:
        t = (year - 1600)
        dt = 120 - 0.9808*t - 0.01532*t**2 + t**3/7129
    elif year >= 500 and year < 1600:
        t = (year-1000)/100.
        dt = 1574.2 - 556.01*t + 71.23472*t**2 + 0.319781*t**3 - 0.8503463*t**4 \
            - 5.050998e-3*t**5 + 8.3572073e-3*t**6
    elif year >= -500 and year < 500:
        t = year/100.
        dt = 10583.6 - 1014.41*t + 33.78311*t**2 - 5.952053*t**3 - 0.1798452*t**4 \
            + 0.022174192*t**5 + 9.0316521e-3*t**6
    elif year < -500:
        t = (year - 1820)/100.
        dt = -20 + 32*t**2
    else: # we shouldn't get here
        dt = 0.
    return dt

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