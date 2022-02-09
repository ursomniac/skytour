
from dateutil.parser import isoparse
from ..session.cookie import get_cookie_defaults

def get_initial_from_cookie(request, initial):
    cookie = request.session.get('user_preferences', None)
    if not cookie: # OK no cookie
        cookie = get_cookie_defaults()
    initial = dict(
        date = isoparse(cookie['utdt_start']).date(),
        time = isoparse(cookie['utdt_start']).time()
    )
    copy_fields = ['location', 'session_length', 'mag_limit', 'hour_angle_range', 'show_planets']
    for k in copy_fields:
        initial[k] = cookie[k]
    return initial

