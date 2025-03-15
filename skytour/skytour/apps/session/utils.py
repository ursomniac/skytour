from dateutil.parser import isoparse
from django.db.models import Case, When
from ..session.cookie import get_cookie_defaults

def get_initial_from_cookie(request, initial):
    cookie = request.session.get('user_preferences', None)
    if not cookie: # OK no cookie
        cookie = get_cookie_defaults()
    initial = dict(
        date = isoparse(cookie['utdt_start']).date(),
        time = isoparse(cookie['utdt_start']).time()
    )
    copy_fields = ['location',]
    for k in copy_fields:
        initial[k] = cookie[k]
    return initial

def get_observing_locations(all, rejected=False):
    qs = all.annotate(
        priority = Case(
            When(status='Active', then=1),
            When(status='Provisional', then=2),
            When(status='Possible', then=3),
            When(status='TBD', then=4),
            When(status='Issues', then=5),
            When(status='Rejected', then=6)
        )
    ).order_by('priority', 'travel_distance')
    if not rejected:
        return qs.exclude(status='Rejected')
    return qs

def get_observing_mode_string(mode, short=False):
    MODE_STRINGS = {
        'N': 'Naked Eye',
        'B': 'Binoculars',
        'S': 'Small Telescope',
        'M': 'Medium Telescope',
        'I': 'Imaging Telescope'
    }
    SHORT_MODE_STRINGS = {'N': 'Nak. Eye', 'B': 'Binoc.', 'S': 'Sm. Tel.', 'M': 'Med. Tel.', 'I': 'Img. Tel.'}
    if mode is None:
        return None
    if mode in 'NBSMI':
        return SHORT_MODE_STRINGS[mode] if short else MODE_STRINGS[mode]
    return 'Unknown'
