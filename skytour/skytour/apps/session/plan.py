import time
from ..dso.models import DSO
from ..solar_system.models import Comet, Planet, Asteroid
from ..utils.timer import compile_times

def start_v2_issue(x):
    if x is None:
        return False
    if 'start' not in x.keys():
        return False
    if 'is_up' not in x.keys():
        return False
    return True 

def get_plan(context, debug=False):
    """
    This creates an observing plan for a UTDT and location.
    """
    cookies = context['cookies']
    times = [(time.perf_counter(), 'Start')]
    show_all = context.get('show_planets', 'visible') == 'all' # redundant? remove?
    location = context['location']

    # Moon
    try:
        moon_session = cookies['moon']['session']
        go = show_all or start_v2_issue(moon_session)
        if go:
            show_moon = moon_session
        else:
            show_moon = None
        context['moon'] = cookies['moon']
        context['show_moon'] = show_moon
        times.append((time.perf_counter(), 'Moon'))
    except:
        pass

    # Planets
    show_planets = []
    for k in cookies['planets'].keys():
        pd = cookies['planets'][k]
        session = pd.get('session')
        # RAD 12 Jan 2022 - don't get planet images to save time
        go = show_all or start_v2_issue(session)
        if go:
            pd['object'] = Planet.objects.get(slug=pd['slug'])
            show_planets.append(pd)
    context['planets'] = show_planets
    times.append((time.perf_counter(), 'Planets'))

    # Asteroids
    show_asteroids = []
    for v in cookies['asteroids']:
        session = v.get('session', None)
        try:
            go = session is None or start_v2_issue(v)
            if go:
                v['object'] = Asteroid.objects.get(slug=v['slug'])
        except:
            pass
        show_asteroids.append(v)

    context['asteroids'] = show_asteroids
    times.append((time.perf_counter(), 'Asteroids'))

    # Comets
    show_comets = []
    for c in cookies['comets']:
        try:
            go = start_v2_issue(c)
            if go:
                c['object'] = Comet.objects.get(pk=c['pk'])
        except:
            pass
        show_comets.append(c)
    context['comets'] = show_comets
    times.append((time.perf_counter(), 'Comets'))

    # DSOs
    targets = {}
    ### BUG: this won't work for latitude < 0!
    all_dsos = DSO.objects.filter(dec__gt=context['dec_limit'], ).order_by('ra')
    for dso in all_dsos:
        if dso.object_is_up(location, context['utdt_start'], min_alt=20.):
            #or dso.object_is_up(location, context['utdt_X_end'], min_alt=0.):
            if dso.priority:
                priority = dso.priority.lower()
                if priority in targets.keys():
                    targets[priority].append(dso)
                else:
                    targets[priority] = [dso]
    context['dso_targets'] = targets
    times.append((time.perf_counter(), 'DSOs'))

    context['times'] = compile_times(times)
    return context
