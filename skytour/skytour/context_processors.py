from django.conf import settings
from .apps.observe.models import ObservingLocation
def get_global_items(request):
    user_preferences = request.session['user_preferences']
    try:
        location = ObservingLocation.objects.get(pk=user_preferences['location'])
    except:
        location = None
    return dict(
        user_preferences=user_preferences,
        location=location
    )