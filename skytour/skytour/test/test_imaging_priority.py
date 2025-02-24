from skytour.apps.dso.models import DSO

def run_all(how='diff'):
    n = 0
    l = []
    dsos = DSO.objects.all()
    for dso in dsos:
        mode = dso.dsoobservingmode_set.filter(mode='I').first()
        if mode is None:
            continue
        old = dso.mode_imaging_priority
        if old is None and how == 'diff':
            continue
        if old is not None and how != 'diff':
            continue
        if old != mode.priority:
            #foo = f"{dso}: Mode: {mode.priority} != Old: {old}"
            foo = f"{dso.pk}\t{dso}\t{mode.viable}\t{mode.priority}\t{old}"
            l.append(foo)
            n += 1
    print(f"{n} Discrepancies found!")
    return l