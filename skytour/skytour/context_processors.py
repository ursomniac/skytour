from dateutil.parser import isoparse
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

    return dict(
        user_preferences=user_preferences,
        location=location,
        utdt_str = utdt_str
    )
