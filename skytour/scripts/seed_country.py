from skytour.apps.misc.models import Country
from skytour.apps.misc.vocabs import COUNTRY_CODE_SEED

def run_country(d):
    c = Country()
    c.name = d[0]
    c.code = d[1]
    c.save()

def run_all():
    for c in COUNTRY_CODE_SEED:
        run_country(c)