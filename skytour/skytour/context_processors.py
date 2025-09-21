from dateutil.parser import isoparse
import datetime as dt
from .apps.observe.models import ObservingLocation
from .apps.session.utils import get_observing_mode_string

def adjust_date(mydate, offset=0):
    this_month = mydate.month
    this_year = mydate.year
    this_month += offset
    if this_month > 12:
        this_month -= 12
        this_year += 1
    elif this_month < 1:
        this_month += 12
        this_year -= 1
    return mydate.replace(month=this_month, year=this_year)

def get_global_items(request):
    user_preferences = request.session.get('user_preferences', None)
    if not user_preferences:
        return dict()
    
    loc_pk = user_preferences.get('location', None)
    if loc_pk:
        location = ObservingLocation.objects.get(pk=user_preferences['location'])
    else:
        location = ObservingLocation.get_default_location()

    ut = isoparse(user_preferences['utdt_start'])
    utdt_str = ut.strftime("%Y-%m-%d %H:%M:%S UT")
    if 'local_time_start' in user_preferences.keys() and user_preferences['local_time_start'] is not None:
        local_time = isoparse(user_preferences['local_time_start'])
    else:
        local_time = dt.datetime.now() 
        local_time_str = None

    local_time_str = local_time.strftime("%a %b %d, %Y  %I:%M %p %z")
    observing_mode = user_preferences.get('observing_mode', 'I')
    observing_mode_string = get_observing_mode_string(observing_mode)
    observing_mode_string_short = get_observing_mode_string(observing_mode, short=True)

    # Set next_month and previous_month
    now = dt.datetime.now(dt.timezone.utc)
    now = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    next_month = adjust_date(now, offset=1)
    previous_month = adjust_date(now, offset=-1)
    this_month = adjust_date(now, offset=0)
    this_year = now.year

    #print("THIS MONTH: ", this_month)
    #print("NEXT MONTH: ", next_month)
    #print("THIS YEAR: ", this_year)

    plot_reversed = False
    if 'color_scheme' in user_preferences.keys():
        plot_reversed = user_preferences.get('color_scheme', 'default') == 'dark'

    return dict(
        user_preferences=user_preferences,
        location=location,
        utdt_str = utdt_str,
        local_time_str = local_time_str,
        cookie_utdt = ut,
        cookie_local = local_time,
        this_year = this_year,
        this_month = this_month,
        next_month = next_month,
        previous_month = previous_month,
        observing_mode = observing_mode,
        observing_mode_string = observing_mode_string,
        observing_mode_string_short = observing_mode_string_short,
        plot_reversed=plot_reversed
    )
