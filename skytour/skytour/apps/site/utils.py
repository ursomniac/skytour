
import datetime
from django.utils.safestring import mark_safe
from ..dso.models import DSO, DSOList, DSOObservation, DSOLibraryImage
from ..session.models import ObservingSession
from ..solar_system.models import (
    Asteroid, AsteroidObservation,
    Comet, CometObservation,
    Planet, PlanetObservation
)

MODEL_BY_SLUG = {'dso': DSO, 'asteroid': Asteroid, 'comet': Comet, 'planet': Planet}
OBS_MODEL_BY_SLUG = {'dso': DSOObservation, 'asteroid': AsteroidObservation, 
    'comet': CometObservation, 'planet': PlanetObservation }
SLUG_LIST = ['dso', 'planet', 'comet', 'asteroid']

def get_number_of_observations_by_model(slug):
    return OBS_MODEL_BY_SLUG[slug].objects.count()

def get_number_of_observed_objects_by_model(slug):
    object_field = 'object'    
    return OBS_MODEL_BY_SLUG[slug].objects.values(object_field).distinct().count()

def observation_table():
    out = '<table><tr><th>Object Type</th><th># Obj.</th><th># Obs.</th></tr>'
    for slug in SLUG_LIST:
        name = slug.title() if slug != 'dso' else 'DSO'
        out += f'<tr><td>{ name }</td>'
        n_obj = get_number_of_observed_objects_by_model(slug)
        out += f'<td class="num">{ n_obj }</td>'
        n_obs = get_number_of_observations_by_model(slug)
        out += f'<td class="num">{ n_obs }</td>'
        out += '</tr>'
    out += '</table>'
    return mark_safe(out)

def get_number_observing_sessions(any=False):
    all_sessions = ObservingSession.objects.all()
    if any:
        return all_sessions.count()
    # only count session where things were observed
    with_objects = []
    for ses in all_sessions:
        na = ses.asteroidobservation_set.count()
        nc = ses.cometobservation_set.count()
        np = ses.planetobservation_set.count()
        nd = ses.dsoobservation_set.count()
        total = na + nc + np + nd
        if total > 0:
            with_objects.append(ses)
    return len(with_objects)

def get_last_observing_session():
    return ObservingSession.objects.first()

def get_most_popular_observing_locations(n=None):
    """ 
    this is the long way...
    """
    all_sessions = ObservingSession.objects.all()
    d = {}
    for ses in all_sessions:
        k = (ses.location.pk, ses.location)
        if k not in d.keys():
            d[k] = 1
        else:
            d[k] += 1
    sorted_list = sorted(d.items(), key=lambda item: item[1], reverse=True)
    if n is None:
        return sorted_list
    if n is not None:
        return sorted_list[:n]
    return sorted_list

def get_random_dso_library_image(style='square', processing='post-processed'):
    image = DSOLibraryImage.objects.filter(
        image_orientation=style, image_processing_status=processing
    ).order_by('?').first()
    return image

def get_active_dso_lists(n=3):
    return DSOList.objects.filter(active=True)[:n]

def number_of_days_since_last_observing_session():
    last_session = get_last_observing_session()
    if last_session is not None:
        today = datetime.date.today()
        delta = today - last_session.ut_date
        return delta.days
    return None

def get_skytour_version():
    lines = None
    try:
        with open('VERSION', 'r') as f:
            lines = f.readlines()
        f.close()
    except:
        pass
    if not lines:
        return '???'
    return lines[0].strip()

def get_active_dso_lists():
    lists = DSOList.objects.filter(active_observing_list=1)
    return lists