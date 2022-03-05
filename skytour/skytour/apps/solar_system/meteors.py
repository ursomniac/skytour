import datetime, pytz
from ..observe.time import get_julian_date
from .models import MeteorShower

def get_meteor_showers(utdt=None):
    if not utdt:
        utdt = datetime.datetime.utcnow().replace(tzinfo=pytz.utc)
    active = []
    jd = get_julian_date(utdt)
    meteor_showers = MeteorShower.objects.all()

    # Make the list
    for s in meteor_showers:
        dstart = datetime.datetime(utdt.year, s.start_date.month, s.start_date.day)
        dend = datetime.datetime(utdt.year, s.end_date.month, s.end_date.day)
        if s.start_date.month == 12 and s.peak_date.month == 1: # quadrantids
            if utdt.month == 12: # ends next year
                dend = datetime.datetime(utdt.year+1, s.end_date.month, s.end_date.day)
            else: # started last year
                dstart = datetime.datetime(utdt.year-1, s.start_date.month, s.start_date.day)
        jd0 = get_julian_date(dstart)
        jd1 = get_julian_date(dend)
        if jd >= jd0 and jd <= jd1:
            active.append(s)

    return active