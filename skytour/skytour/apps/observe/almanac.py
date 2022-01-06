import math
import datetime, pytz
from skyfield.almanac import risings_and_settings, find_discrete, dark_twilight_day
from skyfield.api import wgs84, load
from .time import get_0h

def get_astronomical_twilight(times, events, value):
    """
    value = 0 for end of astronomical twilight
    value = 1 for the beginning of astronomical twilight (first occurrence)
    """
    try:
        zindex = events.tolist().index(value)
        at_time = times[zindex]
    except:
        at_time = None
    return at_time

def dark_time(d, debug=False):
    """
    Given a dict of metadata, get the begin/end of twilight
    """
    f = dark_twilight_day(d['eph'], d['wgs'])
    today = get_0h(d['utdt'])
    end_at, begin_at = get_almanac_times(today, d['ts'], f)
    if debug:
        print ("F: ", f)
        print ("Today: ", today)
        print ("End at: ", end_at)
        print ("Begin at: ", begin_at)
    return end_at, begin_at

def get_almanac_times(today, ts, f):
    """
    Get the beginning and end of Astronomical Twilight for a date
    """
    t0 = ts.from_datetime(today)
    t1 = ts.from_datetime(today + datetime.timedelta(days=1))
    t2 = ts.from_datetime(today + datetime.timedelta(days=2))
    times, events = find_discrete(t0, t1, f)
    end_at = get_astronomical_twilight(times, events, 0)
    times, events = find_discrete(t1, t2, f)
    begin_at = get_astronomical_twilight(times, events, 1)
    return end_at, begin_at


def get_object_rise_set(utdt, eph, target, location):
    """
    Get Rise/Set times for an target from a given location.
    """
    ts = load.timescale()
    loc = wgs84.latlon(location.latitude, location.longitude)
    ut1 = utdt + datetime.timedelta(days=1)
    t0 = ts.utc(utdt.year, utdt.month, utdt.day)
    t1 = ts.utc(ut1.year, ut1.month, ut1.day)

    f = risings_and_settings(eph, target, loc)
    t, y = find_discrete(t0, t1, f)

    events = []
    for zt, zy in zip(t, y):
        if zy == 0: # set
            event_type = 'Set'
        else:
            event_type = 'Rise'
        jd = zt.tt.item()
        ut = zt.utc_datetime()
        # ERROR: This gives UT time still!
        local = zt.astimezone(pytz.timezone(location.time_zone.name))

        events.append(dict(
            type = event_type, 
            jd = jd, 
            ut = ut,
            local = local
        ))
    return events
    