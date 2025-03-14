from skytour.apps.misc.models import StateRegion
from skytour.apps.misc.vocabs import STATE_PROVINCE_SEED

MARKERS = {'ma': 'o', 'vt': 'v', 'ct': '^', 'me': '<', 'ny': 'x', 'pa': '<'}

def fix_state(rec):
    pk = rec[0]
    name = rec[1]
    abbr = rec[2].upper()
    ccode = rec[3]
    slug = f"{ccode.lower()}-{abbr.lower()}"
    marker = 'x'
    if abbr.lower() in MARKERS.keys():
        marker = MARKERS[abbr.lower()]

    s = StateRegion()
    s.pk = pk
    s.name = name
    s.abbreviation = abbr
    s.slug = slug
    s.marker = marker
    s.save()

def run_all():
    for rec in STATE_PROVINCE_SEED:
        fix_state(rec)

