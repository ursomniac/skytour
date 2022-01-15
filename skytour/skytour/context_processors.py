from django.conf import settings
from .apps.observe.models import ObservingLocation

def get_global_items(request):
    """
    
    BROKEN!  This causes things to fail.
    
    """
    user_preferences = request.session.get('user_preferences', None)
    if not user_preferences:
        return None

    loc_pk = user_preferences.get('location', None)
    if loc_pk:
        location = ObservingLocation.objects.get(pk=user_preferences['location'])
    return dict(
        user_preferences=user_preferences,
        location=location
    )
