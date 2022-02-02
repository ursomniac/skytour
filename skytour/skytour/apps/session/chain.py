from itertools import chain
from ..dso.models import DSOObservation
# from .solar_system.models import PlanetObservation, AsteroidObservation, CometObservation

def get_all_observations(ut_date): # or start/end date/time?
    """
    This is a placeholder for when I have things to log.
    I THINK this would combine all the different models under one list, 
    for the case of "What did I observe the night of 15-Jun-2022?"

    For logs of observations of a particular DSO or planet, etc., then
    that's easily obtainable through the "observing_log.all()" call from
    the DSO/Planet/etc.   

    I suppose this could ALSO be useful for other filters, e.g., 
    "what magnitudes did I look at on nights where the seeing was good",
    but that sort of stuff will come later.

    I'm expecting that how this will WORK is that I'll log things on paper,
    then add it in through the admin ex post facto.
    """
    dsos = DSOObservation.objects.filter(ut_date = ut_date)
    planets, asteroids, comets = None # for now
    # planets = PlanetObservation.objects.filter(ut_date = ut_date)
    # asteroids = AsteroidObservation.objects.filter(ut_date = ut_date)
    # comets = CometObservations.filter(ut_date = ut_date)
    observation_list = sorted(
        chain(dsos, planets, comets, asteroids),
        key=lambda obs: obs.ut_time)
    return observation_list