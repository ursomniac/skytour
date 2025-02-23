from skytour.apps.dso.models import DSO

def haz(x):
    if x is None:
        return ''
    return str(x)

def pri(x):
    if x is None:
        return None
    return x.priority

# Goals
#   1. look for mode gaps
#   2. P(S) == P(M) == P(O)
#       
def run_all():
    lines = []
    dsos = DSO.objects.all()
    for dso in dsos:
        modes = dso.dsoobservingmode_set.all()
        mode_s = pri(modes.filter(mode='S').first())
        mode_m = pri(modes.filter(mode='M').first())
        mode_o = dso.priority_value

        if mode_o == mode_m == mode_s:          # nothing to fix
            continue 
        if mode_o is None and (mode_m == mode_s): # nothing to fix - that's OK too
            continue
        if mode_o == 0 and (mode_m == mode_s): # not as good but OK:
            continue
        if mode_m is None and mode_s is None: # this isn't an optical object!
            continue
        # mode_o != (mode_s | mode_m) or mode_s != mode_m --- want to check this
        out = [haz(dso.pk), dso.shown_name, haz(mode_o), haz(mode_s), haz(mode_m)]
        line = '\t'.join(out)
        lines.append(line)
    return lines

def get_situation(s = None, m = None, p = None):
    dsos = DSO.objects.order_by('pk')
    out = []
    for dso in dsos:
        mode_s = dso.dsoobservingmode_set.filter(mode='S').first()
        pri_s = None if mode_s is None else mode_s.priority
        mode_m = dso.dsoobservingmode_set.filter(mode='M').first()
        pri_m = None if mode_m is None else mode_m.priority
        if (pri_s != s) or (pri_m != m) or (dso.priority != p):
            continue
        out.append(dso)
    return out