import datetime
from skyfield import api
from ..observe.almanac import get_sun_rise_set, get_moon_rise_set, get_twilight_begin_end
from ..observe.models import ObservingLocation
from ..observe.time import get_julian_date
from ..site_parameter.helpers import find_site_parameter
from ..solar_system.moon import simple_lunar_phase
from .models import Calendar

def get_upcoming_calendar(now, range=[-2, 5]):
    r0 = (now + datetime.timedelta(days=range[0])).date()
    r1 = (now + datetime.timedelta(days=range[1])).date()
    events = Calendar.objects.filter(date__range=[r0, r1]).order_by('date')
    return events

PHASE_ABBR = {
    'NEW': 'NM', 
    'WAXING CRESCENT': 'WxC',
    'FIRST QUARTER': 'FQ', 
    'WAXING GIBBOUS': 'WxG',
    'FULL': 'FM', 
    'WANING GIBBOUS': 'WnG', 
    'LAST QUARTER': 'LQ', 
    'WANING CRESCENT': 'WnC'
}

def create_calendar_grid(start_date, location_pk = None, days_out=30, time_zone=None):
    """
    Create a list of weeks, which itself is a list of 7 days.
    Populate each [week, day] with information.
    Return the grid.
    """
    if type(start_date) == datetime.datetime:
        t0 = start_date
    elif type(start_date) == tuple:
        (year, month, day) = start_date
        t0 = datetime.datetime(year, month, day, 0, 0)
    else:
        return None

    t1 = t0 + datetime.timedelta(days=days_out)

    # Get events from the Calendar model
    events = Calendar.objects.filter(date__range=[t0.date(), t1.date()]).order_by('date')
    week_number = 0
    cells = []

    # Set up rise/set, AT start/end
    ts = api.load.timescale()
    eph = api.load('de421.bsp')
    if location_pk is None:
        location_pk = find_site_parameter('default-location-id', 43, 'positive')
    location = ObservingLocation.objects.get(pk=location_pk)
    loc = api.wgs84.latlon(location.latitude, location.longitude)

    # Create a list of data, one for each day shown
    for i in range(days_out + 1):
        tt = t0 + datetime.timedelta(days=i)
        ee = events.filter(date=tt.date())
        wd = tt.isoweekday() % 7 # Sun = 0, Sat = 6
        jd = get_julian_date(tt)
        moon = simple_lunar_phase(jd)
        moon['phase_abbr'] = PHASE_ABBR[moon['phase']]

        # sunrise, sunset
        sunrise, sunset = get_sun_rise_set(tt, loc, ts, eph, time_zone=time_zone)
        # AT start, end
        twilight = get_twilight_begin_end(tt, location, time_zone=time_zone)
        # moonrise, moonset
        moonrise, moonset = get_moon_rise_set(tt, location, eph, time_zone=time_zone)

        cell_dict = dict(
            date = tt.date(),
            events = ee,
            day_of_week = wd,
            week = week_number,
            jd = int(jd),
            moon = moon,
            sunset = sunset,
            sunrise = sunrise,
            moonrise = moonrise,
            moonset = moonset,
            twilight = twilight
        )
        # If the next day is a Sunday, start a new week
        if wd == 6:
            week_number += 1
        cells.append(cell_dict)

    # Oops! Decrement week_number if we ended on a Saturday
    if wd == 6:
        week_number -= 1

    # Turn the list into a grid
    grid = []
    # Create the grid with all cells = None
    for i in range(week_number+1):
        grid.append([None]*7)
    # Now fill them in
    for cell in cells:
        week = cell['week']
        day = cell['day_of_week']
        grid[week][day] = cell
        
    return grid

