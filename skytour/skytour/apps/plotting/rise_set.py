import matplotlib
from matplotlib.font_manager import ttfFontProperty
from skyfield.api import load, wgs84
from skyfield.almanac import risings_and_settings, find_discrete
from ..observe.models import ObservingLocation
from ..session.cookie import get_cookie
from ..solar_system.models import Planet, Asteroid, Comet

def show_rise_set(utdt_start, utdt_end, name, obj_type='planet', location_id=43, tz='US/Eastern'):
    location = ObservingLocation.objects.get(pk=location_id)
    observer = wgs84.latlon(location.latitude, location.longitude)
    ts = load.timescale()

    start = ts.utc(utdt_start.year, utdt_start.month, utdt_start.day)
    end = ts.utc(utdt_end.year, utdt_end.month, utdt_end.day)
    eph = load('de421.bsp')

    f = risings_and_settings(eph, eph[name], observer)
    t, y = find_discrete(start, end, f)

    t_rise = t[(y==1)]
    t_set = t[(y==0)]

    return t_rise, t_set

