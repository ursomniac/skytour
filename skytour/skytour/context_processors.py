from dateutil.parser import isoparse
import datetime as dt
from .apps.observe.models import ObservingLocation

def get_global_items(request):
    user_preferences = request.session.get('user_preferences', None)
    if not user_preferences:
        return dict()
    loc_pk = user_preferences.get('location', None)
    if loc_pk:
        location = ObservingLocation.objects.get(pk=user_preferences['location'])
    ut = isoparse(user_preferences['utdt_start'])
    utdt_str = ut.strftime("%Y-%m-%d %H:%M:%S UT")
    if 'local_time_start' in user_preferences.keys() and user_preferences['local_time_start'] is not None:
        local_time = isoparse(user_preferences['local_time_start'])
    else:
        local_time = dt.datetime.now() # This will come back as UTC because the server is set to that.
        local_time_str = None
    local_time_str = local_time.strftime("%b %d, %Y  %I:%M %p %Z")

    return dict(
        user_preferences=user_preferences,
        location=location,
        utdt_str = utdt_str,
        local_time_str = local_time_str,
        cookie_utdt = ut,
        cookie_local = local_time,
    )
