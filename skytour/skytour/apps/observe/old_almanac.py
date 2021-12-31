import datetime as dt
import math
from skyfield import almanac
from ..solar_system.planets import get_solar_system_object
from ..utils.format import to_sex
from .time import get_0h, estimate_delta_t, get_gmst0

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
    f = almanac.dark_twilight_day(d['eph'], d['wgs'])
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
    t1 = ts.from_datetime(today + dt.timedelta(days=1))
    t2 = ts.from_datetime(today + dt.timedelta(days=2))
    times, events = almanac.find_discrete(t0, t1, f)
    end_at = get_astronomical_twilight(times, events, 0)
    times, events = almanac.find_discrete(t1, t2, f)
    begin_at = get_astronomical_twilight(times, events, 1)
    return end_at, begin_at

def construct_obs_list(utdt_list, object_name):
    """
    For each UTDT in the list, get the position of something.
    Useful for rise/set calculations - possibly could work for tracking things across the sky too!
    """
    obs_dict = []
    for u in utdt_list:
        z = {}
        (ra, dec, dist) = get_solar_system_object(u, object_name).radec()
        z['ra_deg'] = ra.hours.item() * 15.
        z['ra_rad'] = math.radians(z['ra_deg'])
        z['ra_h'] = ra.hours.item()
        z['dec_deg'] = dec.degrees.item()
        z['dec_rad'] = math.radians(z['dec_deg'])
        obs_dict.append(z)
    return obs_dict

def rectify_m(m):
    """
    m should be between 0 and 1.
    """
    if m < 0.:
        x = m + 1.
    elif m > 1.:
        x = m - 1.
    else: 
        x = m
    return x

def interpolate(obs, n):
    """
    See Meeus, 2nd Ed.  Chapter 3, formula 3.3.
    """
    # Interpolation formula:
    #    y = y1 + ( n * (a + b + n*c)/2 )
    # where:
    #   a = y1-y0
    #   b = y2-y1
    #   c = b - a
    #   n is the provided interpolating factor for (transit, rise, set)
    #
    # This is a grid across n (transit, rise, set) and the three moon values
    idx = ['transit', 'rise', 'set']
    c = ['ra', 'dec']
    v = ['ra_deg', 'dec_deg']
    vals = {}
    for x in idx:
        vals[x] = {}
    #print ("OBS: ", obs)
    for k1, k2 in zip(c, v):
        y1 = obs[1][k2]
        a = obs[1][k2] - obs[0][k2]
        b = obs[2][k2] - obs[1][k2]
        c = b - a
        for i in range(3):
            vals[idx[i]][k1] = y1 + (n[i] * (a + b + n[i]*c)/2. )
    #print("VALS: ", vals)
    return vals

def iterate_on_m(m_list, obs,  delta_t, gast0, lat_rad, lon_deg, h0):
    """ 
    Using the local sidereal time for each event, adjust m, and calculate a new ∆m.
    """
    # sidereal times for each event
    theta0 = [(gast0 + 360.985_647 * m) for m in m_list]
    # adjust m for the sidereal time -> n
    n_list = [m + delta_t/86400 for m in m_list]
    # use n to get the ra/dec at these times
    coord_dict = interpolate(obs, n_list)

    # OK from here:
    i = 0
    # Create the next iteration of the list of m's.
    new_m_list = []
    delta_m_list = []
    # Loop through transit/rise/site
    for k, v in coord_dict.items(): # transit, rise, set
        # Get local hour angles
        hh = (theta0[i] - lon_deg - v['ra'])  # degrees
        hh_rad = math.radians(hh)
        dec_rad = math.radians(v['dec'])
        # Get ∆m for each event
        if k != 'transit': # rise, set
            t1 = math.sin(lat_rad) * math.sin(dec_rad) 
            t2 = math.cos(lat_rad) * math.cos(dec_rad) * math.cos(hh_rad)
            h = math.degrees(math.asin(t1 + t2))
            delta_m = (h - h0) / (360. * math.cos(dec_rad) * math.cos(lat_rad) * math.sin(hh_rad)) # degrees
        else: # transit
            delta_m = -1. * hh / 360.
        # new m += ∆m
        m = m_list[i] + delta_m
        #print ("{}: M: {} ∆m: {} new M {}".format(k, m_list[i], delta_m, m))
        new_m_list.append(m)
        delta_m_list.append(delta_m)
        i += 1
    # return the new list of m's and the ∆m values
    return new_m_list, delta_m_list

def get_object_rise_set(utdt0, object_name, location, debug=False):
    """
    From Meeus, 2nd Ed. p. 102
    This is only good to a few minutes.
    """
    # Start with the date at UT = 0h
    utdt = utdt0.replace(hour=0, minute=0, second=0, microsecond=0)
    # Sidereal time at Greenwich 0h.
    gast0 = get_gmst0(utdt, format='degrees')

    # Location coordinates in degrees and radians
    #   since different equations use either.
    lat_deg = location.latitude
    lat_rad = math.radians(lat_deg)
    lon_deg = -location.longitude # MEASURED POSITIVE WEST!

    # ∆T estimation for date (in seconds)
    delta_t = estimate_delta_t(utdt0) # Correction for dynamical time
    # Get the "standard" altitude (i.e., the geometric altitude for the body) at rise/set.
    if object_name == 'moon':
        little_h0 = 0.125 # approximate degrees shoud be 0.7275 * parallax - 0.34
    else:
        little_h0 = -0.5667 # degrees
        little_h0_rad = math.radians(little_h0)

    # Get the UTDT for the day before and the day after - this is for interpolation later on.
    utdt_list = [utdt - dt.timedelta(1), utdt, utdt + dt.timedelta(1)]
    
    # Get the object's position for each of the time utdt values
    obs_list = construct_obs_list(utdt_list, object_name)
    
    # Convenience for the trig later on
    dec_rad = obs_list[1]['dec_rad']
    ra_deg = obs_list[1]['ra_deg']

    # This is the hour angle of the object at the horizon (+ is set, - is rise)
    # If cos(H0) is outside ± 1 then either the moon is always or never aobve the horizon
    #   and the concept of rise/set is meaningless.
    t1 = math.sin(little_h0_rad) - (math.sin(lat_rad) * math.sin(dec_rad))
    t2 = math.cos(lat_rad) * math.cos(dec_rad)
    cos_ha0 = t1 / t2
    if cos_ha0 > 1.:
        return {'rise': None, 'set': None, 'flag': "Always above horizon"}
    elif cos_ha0 < -1.:
        return {'rise': None, 'set': None, 'flag': "Never above horizon"}
    ha0 = math.degrees(math.acos(cos_ha0))
    #print("cos HA0", cos_ha0, "HA0: ", ha0)

    # OK these are the times (expressed in partial days) for transit/rise/set
    # They're in the range 0 to 1.
    m0 = rectify_m((ra_deg + lon_deg - gast0) / 360.) # transit
    m1 = rectify_m(m0 - (ha0 / 360.))                 # rise
    m2 = rectify_m(m0 + (ha0 / 360.))                 # set
    m_list = [m0, m1, m2]

    # We're going to iterate updating m_list until the changes are negligible.
    iteration = 1
    done = False
    # Iterate up to 5 times or until the avg change in ∆m is ≤ 3s.
    while iteration <= 5 and not done:
        (m_list, delta_m_list) = iterate_on_m(m_list, obs_list, delta_t, gast0, lat_rad, lon_deg, little_h0)
        avg_delta = sum(delta_m_list) / len(delta_m_list)
        if abs(avg_delta) <  (1./28800.): # 3 seconds
            done = True
        iteration += 1

    # OK m_list has our final answer.  Convert to times.
    d = {
        'transit': to_sex((m_list[0] * 24.) % 24., format('hms')),
        'rise':    to_sex((m_list[1] * 24.) % 24., format('hms')),
        'set':     to_sex((m_list[2] * 24.) % 24., format('hms')),
    }
    return d
