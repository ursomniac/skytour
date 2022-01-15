import datetime, pytz
from dateutil.parser import isoparse
from ..observe.models import ObservingLocation
from ..observe.time import get_julian_date, get_t_epoch

def get_cookie_defaults():
    ut0 = datetime.datetime.utcnow().replace(tzinfo=pytz.utc)
    session_length = 3 # TODO: Set this in the Admin
    ut1 = ut0 + datetime.timedelta(hours=session_length)
    julian_date = get_julian_date(ut0)
    t = get_t_epoch(julian_date)

    cookie_dict = dict (
        utdt_start = ut0.isoformat(),
        utdt_end = ut1.isoformat(),
        session_length = session_length,
        location = 43, # TODO: Set this in the Admin!
        dec_limit = -20., # TODO: Set this in the Admin!
        mag_limit = 12.0, # TODO: Set this in the Admin!
        hour_angle_range = 3.5, # TODO: Set this in the Admin!
        show_planets = 'visible', # TODO: Set this in the Admin!
        julian_date = julian_date,
        t = t
    )
    return cookie_dict

def deal_with_cookie(request, context):
    # First - do we have a cookie?
    cookie = request.session.get('user_preferences', None)
    if not cookie: # OK no cookie - SET things to a default
        cookie = get_cookie_defaults()
        request.session['user_preferences'] = cookie

    for k, v in cookie.items():
        context[k] = v
    # Override these three values from the cookie where they're encoded
    context['utdt_start'] = isoparse(cookie['utdt_start'])
    context['utdt_end'] = isoparse(cookie['utdt_end'])
    context['location'] = ObservingLocation.objects.filter(pk=cookie['location']).first()
    return context
