# TODO: 
# DONE 1. Get the midnight culmination date for an object (ra, dec) (location invariant)
# DONE 2. Get the culmination date for an object (ra, dec) at a given UT (ditto?)
# 3. Get the range of dates for an object to be above the horizon at a given location
#   3.1. this might be none or circumpolar
# 4. Get the range of dates for an object to be above a given altitude at a given location
#   4.1. This might be null or circumpolar
# 5. Get date range for an object above a given altitude at a location at a time of day.

import datetime as dt
import math
from .time import get_utdt, get_gmst0

OFFSET = 1.00273790935
YEAR_OFFSET = 365 * OFFSET

# RA = LST at meridian
def get_opposition_date(ra, debug=False, next=True):
    utdt = get_utdt() # current UTDT
    gmst0 = get_gmst0(utdt) # GMST at 0h
    ha = ra - gmst0 % 24.
    delta_days = 365 * ha / 24.
    if next and delta_days < 0:
        delta_days += YEAR_OFFSET # TODO: IS THIS RIGHT?
    opposition = utdt + dt.timedelta(days = int(delta_days))

    if debug:
        print ("RA: ", ra)
        print ("GMST0: ", gmst0)
        print ("HA: ", ha)
        print ("OPP: ", opposition)
    return opposition # next opposition

def get_hms(x):
    sign = 1. if x >= 0. else -1.
    x = abs(x)
    h = int(x)
    x = (x - h) * 60.
    m = int(x)
    x = (x - m) * 60.
    s = int(x)
    x = (x - s) * 1e6
    micro = int(x)
    return h, m, s, micro


def get_opposition_date_at_time(ra, hours, next=True):
    # hours is LOCAL standard time
    (zh, zm, zs, zz) = get_hms(hours)
    date0 = get_opposition_date(ra)
    delta = 365 * hours / 24.
    if next and delta < 0:
        delta -= YEAR_OFFSET
    date1 = date0 - dt.timedelta(days = int(delta))
    new_date = date1.replace(hour=zh, minute=zm, second=zs, microsecond=zz)
    return new_date


def get_max_altitude(dec, latitude, raw=False):
    z = 90 - latitude + dec
    # if z > 90 then it's circumpolar
    # if z < 0 then it never rises
    if not raw:
        if z > 90.:
            z -= 90. # max altitude against opposite horizon
    return z

STD_ALT = math.sin(math.radians(-0.5667))
def get_ha_range(latitude, dec):
    xlat = math.radians(latitude)
    xdec = math.radians(dec)
    t1 = math.sin(xlat) * math.sin(xdec)
    t2 = math.cos(xlat) * math.cos(xdec)
    cos_h0 = (STD_ALT*0. - t1) / t2
    if cos_h0 >= 1.: # never rises
        h0 = None
        sit = 'Never Rises'
    elif cos_h0 < -1.: # never rises
        h0 = None
        sit = 'Circumpolar'
    else:
        h0 = math.degrees(math.acos(cos_h0)) / 15.
        sit = 'Observable'
    return h0, sit

def get_observable_date_range(ra, dec, latitude, debug=False):
    ha, situation = get_ha_range(dec, latitude)
    date0 = get_opposition_date(ra)
    if ha is not None:
        date_start = get_opposition_date(ra-ha % 24.)
        date_end = get_opposition_date(ra+ha % 24.)
        if date_end < date0:
            date_end = date_end + dt.timedelta(days=YEAR_OFFSET)
        if debug:
            print("HA: {:.3f} Start: {} Upper Cul: {}  End: {}".format(ha, date_start, date0, date_end))
    else:
        date_start = None
        date_end = None
        print("{}: {}".format(date0, situation))
    return date_start, date0,  date_end, situation