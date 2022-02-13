import datetime, pytz
from dateutil.parser import isoparse
from ..observe.models import ObservingLocation
from ..observe.time import get_julian_date, get_t_epoch
from ..site_parameter.helpers import find_site_parameter 

def get_cookie_defaults():
    ut0 = datetime.datetime.utcnow().replace(tzinfo=pytz.utc)
    session_length = find_site_parameter('observing-session-length', default=3.0, param_type='float')
    ut1 = ut0 + datetime.timedelta(hours=session_length)
    julian_date = get_julian_date(ut0)
    t = get_t_epoch(julian_date)

    default_location_pk = ObservingLocation.objects.first().pk

    cookie_dict = dict (
        utdt_start = ut0.isoformat(),
        utdt_end = ut1.isoformat(),
        session_length = session_length,
        location = find_site_parameter('default-location-id', default=default_location_pk, param_type='positive'),
        dec_limit = find_site_parameter('declination-limit', default=-25., param_type='float'),
        mag_limit = find_site_parameter('dso-magnitude-limit', default=12.0, param_type='float'),
        hour_angle_range = find_site_parameter('hour-angle-range', default=3.5, param_type='float'),
        show_planets = find_site_parameter('poll-planets', default='visible', param_type='string'),
        julian_date = julian_date,
        t = t,
        visible_asteroids = []
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

def update_cookie_with_asteroids(request, asteroid_list):
    """ 
    TODO: Do we still need this?
    """
    if len(asteroid_list) > 0:
        asteroid_slugs = [x['slug'] for x in asteroid_list]
        request.session['user_preferences']['visible_asteroids'] = asteroid_slugs
        foo = request.session.get('user_preferences', None)
        return asteroid_slugs
    return None