from ..apps.session.models import ObservingSession
from ..apps.dso.models import DSOObservation
from ..apps.solar_system.models import PlanetObservation, CometObservation, AsteroidObservation
import datetime as dt
import pytz

def get_closest_session(sessions, obs, commit=False, debug=False):
    uttz = pytz.timezone('UTC')
    closest = None
    abs_delta = None
    obs_ut = obs.ut_datetime
    for s in sessions:
        s_ut = dt.datetime.combine(s.ut_date, dt.time(0,0)).replace(tzinfo=uttz)
        delta = abs((s_ut - obs_ut).total_seconds())
        if delta < 43200:
            if closest is None or delta < abs_delta:
                closest = s
                abs_delta = delta
                if debug:
                    print(f"{obs.pk}: Setting closest to {s_ut} at {abs_delta} for {obs_ut}")
        if commit:
            obs.session = closest
            obs.save()
    if closest is None:
        print(f"{obs.pk}: could not find session for {obs_ut}")
    return closest, abs_delta

def run_list(type=None, commit=False):
    sessions = ObservingSession.objects.all()
    obs_list = None
    if type == 'dso':
        obs_list = DSOObservation.objects.all()
    elif type == 'planet':
        obs_list = PlanetObservation.objects.all()
    elif type == 'asteroid':
        obs_list = AsteroidObservation.objects.all()
    elif type == 'comet':
        obs_list = CometObservation.objects.all()
    if obs_list is not None:
        for o in obs_list:
            sesh, delta = get_closest_session(sessions, o, commit=commit, debug=True)
