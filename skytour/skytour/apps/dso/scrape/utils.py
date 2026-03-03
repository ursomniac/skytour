
def get_id(obj, model):
    return f"{model}{obj.pk:05d}"

def convert_ra(t):
    try:
        ra = int(t[0]) + 0.
        ra += int(t[1]) / 60.
        ra += float(t[2]) / 3600.
        return ra
    except:
        return None
    
def convert_dec(t):
    try:
        d = int(t[1]) + 0.
        d += int(t[2]) / 60.
        d += float(t[3]) / 3600.
        d *= -1. if t[0] == '-' else 1.
        return d
    except:
        return None
    
def get_ocl(dso):
    if dso.simbad and type(dso.simbad) == dict and 'aliases' in dso.simbad.keys():
        m = [s for s in dso.simbad['aliases'] if s.startswith('OCl')]
        if len(m) == 1:
            return m[0]
        elif len(m) > 1:
            mm = [x for x in m if '.0' not in x]
            return mm[0]    
    return None
