import datetime, pytz
from dateutil.parser import isoparse
from ..misc.models import TimeZone
from ..observe.models import ObservingLocation
from ..astro.time import get_julian_date, get_t_epoch
from ..site_parameter.helpers import find_site_parameter 

def test_all_cookies(cookies):
    for key in ['planets', 'asteroids', 'comets', 'moon', 'sun']:
        if key not in cookies.keys():
            return False
        if cookies[key] is None:
            return False
    return True
    
def get_all_cookies(request):
    user_pref = deal_with_cookie(request, {})
    planets = get_cookie(request, 'planets')
    asteroids = get_cookie(request, 'asteroids')
    comets = get_cookie(request, 'comets')
    moon = get_cookie(request, 'moon')
    sun = get_cookie(request, 'sun')
    cookies = dict(
        planets = planets,
        asteroids = asteroids,
        comets = comets,
        moon = moon,
        sun = sun,
        user_pref = user_pref
    )
    return cookies

def get_cookie_defaults():
    ut0 = datetime.datetime.now(datetime.timezone.utc)
    julian_date = get_julian_date(ut0)
    t = get_t_epoch(julian_date)

    cookie_dict = dict (
        utdt_start = ut0.isoformat(),
        location = ObservingLocation.get_default_location().pk,
        color_scheme = 'dark',
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
    context['location'] = ObservingLocation.objects.filter(pk=cookie['location']).first()
    context['time_zone'] = context['location'].time_zone.pytz_label
    context['local_time'] = context['utdt_start'] #.astimezone(pytz.timezone(context['time_zone']))
    context['local_time_str'] = context['local_time'].strftime('%a %b %-d, %Y %-I:%M %p %z')
    return context

def get_cookie(request, slug):
    cookie = request.session.get(slug, None)
    return cookie