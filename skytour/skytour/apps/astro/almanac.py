import datetime, pytz
from skyfield.almanac import (
        risings_and_settings, 
        find_discrete, 
        dark_twilight_day, 
        sunrise_sunset, 
        meridian_transits,
        TWILIGHTS
    )
from skyfield.api import wgs84, load
from .time import get_0h
from ..site_parameter.helpers import get_ephemeris

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
    today = get_0h(d['utdt_start'])
    end_at, begin_at = get_almanac_times(today, d['ts'], f)
    if debug:
        print ("F: ", f)
        print ("Today: ", today)
        print ("End at: ", end_at)
        print ("Begin at: ", begin_at)
    return end_at, begin_at

def get_dark_time(utdt, location, debug=False):
    ts = load.timescale()
    wgs = wgs84.latlon(location.latitude, location.longitude)
    eph = load(get_ephemeris())
    f = dark_twilight_day(eph, wgs)
    if debug:
        print(f"TS: {ts}  F: {f}")
    today = get_0h(utdt)
    end_at, begin_at = get_almanac_times(today, ts, f)
    if end_at is None:
        end_at, _ = get_almanac_times(get_0h(utdt - datetime.timedelta(days=-1)), ts, f)
    if begin_at is None:
        _, begin_at = get_almanac_times(get_0h(utdt + datetime.timedelta(days=1)), ts, f)
    if end_at is None:
        print("ERROR Getting end_at dark time!")
    else:
        print("Found end_at dark time ", end_at)
    if begin_at is None:
        print("ERROR getting begin_at dark time!")
    else:
        print("Found begin_at dark time ", begin_at)
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

def get_events(t, y, events=None, transit=False, serialize=False, time_zone=None):
    if events is None:
        events = []
    for zt, zy in zip(t, y):
        if zy == 0: # set or meridian
            event_type = 'Anti-Transit' if transit else 'Set' 
        else:
            event_type = 'Transit' if transit else 'Rise'
        jd = zt.tt.item()
        ut = zt.utc_datetime()
        local_time = zt.astimezone(time_zone) if time_zone is not None else None
        if serialize:
            ut = ut.isoformat()
            local_time = local_time.astimezone(time_zone).isoformat()
        events.append(dict(
            type = event_type, 
            jd = jd, 
            ut = ut,
            local_time = local_time
        ))
    return events

def get_object_rise_set(utdt, eph, target, location, serialize=False, time_zone=None):
    """
    Get Rise/Set times for an target from a given location.
    """
    ts = load.timescale()
    loc = wgs84.latlon(location.latitude, location.longitude)
    ut1 = utdt + datetime.timedelta(days=1)
    t0 = ts.utc(utdt)
    t1 = ts.utc(ut1)

    # Comets do not work...
    # Look at https://rhodesmill.org/skyfield/examples.html#when-is-a-body-or-fixed-coordinate-above-the-horizon
    # to see about a possible solution
    # It's probably as simple as changing target to be a Star() call - yes, comets ARE moving, but if they're
    # near the horizon anyway you won't want to observe them.
    f = risings_and_settings(eph, target, loc)
    t, y = find_discrete(t0, t1, f)
    events = get_events(t, y, serialize=serialize, time_zone=time_zone)

    # TODO: Add transit times!
    f2 = meridian_transits(eph, target, loc)
    t2, y2 = find_discrete(t0, t1, f2)
    events = get_events(t2, y2, events=events, serialize=serialize, time_zone=time_zone, transit=True)
    return events
    
def get_sun_rise_set(utdt, loc, ts, eph, time_zone=None):
    sunrise = None
    sunset = None
    t0 = utdt + datetime.timedelta(hours=2)
    t1 = t0 + datetime.timedelta(days=1)
    zt0 = ts.utc(t0)
    zt1 = ts.utc(t1)

    t, y = find_discrete(zt0, zt1, sunrise_sunset(eph, loc))
    for zt, zy in zip(t, y):
        if zy == 1: # sunrise
            ut = zt.utc_datetime()
            if time_zone is not None:
                local = ut.astimezone(time_zone)
            sunrise = dict(ut = ut, local = local, local_str = local.strftime("%I:%M %p"))
        else:
            ut = zt.utc_datetime()
            if time_zone is not None:
                local = ut.astimezone(time_zone)
            sunset = dict(ut = ut, local = local, local_str = local.strftime("%I:%M %p"))
    return sunrise, sunset

def get_moon_rise_set(utdt0, loc, eph, time_zone=None):
    utdt = datetime.datetime(utdt0.year, utdt0.month, utdt0.day, 2, 0).replace(tzinfo=pytz.utc)
    moon = get_object_rise_set(utdt, eph, eph['moon'], loc, time_zone=time_zone)
    moonrise = None
    moonset = None
    for e in moon:
        ut = e['ut']
        local = e['local_time']
        local_str = local.strftime("%I:%M %p")
        d = dict(ut=ut, local=local, local_str=local_str)
        if e['type'] == 'Rise':
            moonrise = d
        elif e['type'] == 'Set':
            moonset = d
    return moonrise, moonset
            
def get_twilight_begin_end(utdt, loc, time_zone=None):
    twi_list = ['night', 'astro', 'nautical', 'civil', 'day']
    twilight = {}
    
    for tw in twi_list:
        twilight[tw] = dict(start=None, end=None)

    ut0 = utdt.replace(hour=2, minute=0, second=0, microsecond=0)
    ut1 = ut0 + datetime.timedelta(days=1)

    ts = load.timescale()
    t0 = ts.from_datetime(ut0)
    t1 = ts.from_datetime(ut1)
    eph = load(get_ephemeris())
    wgs = wgs84.latlon(loc.latitude, loc.longitude)
    f = dark_twilight_day(eph, wgs)
    times, events = find_discrete(t0, t1, f)

    for t, e in zip(times, events):
        local_time = t.astimezone(time_zone)
        side = 'am' if local_time.hour < 12 else 'pm'
        skey = 'start' if side == 'pm' else 'end'
        twilight[twi_list[e]][skey] = local_time.strftime("%I:%M %p")

    return twilight