import datetime, pytz
from itertools import chain
from ..dso.models import DSOObservation
from ..site_parameter.helpers import find_site_parameter
from ..solar_system.models import PlanetObservation, AsteroidObservation, CometObservation
#from .models import ObservingCircumstances

def get_all_observations(ut_date, circumstances): # or start/end date/time?
    """
    Get all observations from the DSO/Planet/Asteroid/Comet *Observation models
    that fall within the realm of a ObservingSession date.
    """
    # Slice back a few hours to capture the changeover to 0h UT
    # For me, that's -3 hours - it would be different for people in different locations
    # So, create the ability to set that in SiteParameters
    offset_ut = find_site_parameter('session_ut_offset', default=-3, param_type='float')
    # Do the same for the length of the observing window
    # This will get weird for extreme latitudes (esp., > ±62°)
    nighttime_window = find_site_parameter('session_window_hours', default=14, param_type='positive')
    # Get the datetime for the possible observing window:  for me
    #   start = date 0H - 3 hours = 21:00 UT or 16:00 standard time (17:00 daylight)
    #   end = start + 15 hours = 12:00 UT or 7:00 standard time  (8:00 daylight)
    # I THINK this handles all the edge effects.
    utdt_start = (datetime.datetime.combine(ut_date, datetime.time(0,0)) + datetime.timedelta(hours=offset_ut)).replace(tzinfo=pytz.utc)
    utdt_end = (utdt_start + datetime.timedelta(hours=nighttime_window)).replace(tzinfo=pytz.utc)

    # OK get all DSO/Planet/Asteroid/Comet observations that fall within the window.
    #conditions = ObservingCircumstances.objects.filter(ut_datetime__gte = utdt_start, ut_datetime__lte = utdt_end)
    dsos = DSOObservation.objects.filter(ut_datetime__gte = utdt_start, ut_datetime__lte = utdt_end)
    planets = PlanetObservation.objects.filter(ut_datetime__gte = utdt_start, ut_datetime__lte = utdt_end)
    asteroids = AsteroidObservation.objects.filter(ut_datetime__gte = utdt_start, ut_datetime__lte = utdt_end)
    comets = CometObservation.objects.filter(ut_datetime__gte = utdt_start, ut_datetime__lte = utdt_end)
    observation_list = sorted(
        chain(circumstances, dsos, planets, comets, asteroids),
        key=lambda obs: obs.ut_datetime)
    return observation_list