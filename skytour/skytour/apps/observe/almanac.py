import math
import datetime, pytz
from skyfield.almanac import risings_and_settings, find_discrete
from skyfield.api import wgs84, load

def get_object_rise_set(utdt, eph, target, location):
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
            event_type = 'set'
        else:
            event_type = 'rise'
        jd = zt.tt.item()
        ut = zt.utc_datetime()
        local = zt.astimezone(pytz.timezone(location.time_zone))

        events.append(dict(
            type = event_type, 
            jd = jd, 
            ut = ut,
            local = local
        ))
    return events
    