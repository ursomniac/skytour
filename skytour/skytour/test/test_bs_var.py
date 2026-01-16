from skytour.apps.stars.models import BrightStar, VariableStar
from skytour.apps.utils.models import Constellation
from skytour.apps.stars.vocabs import VARDES

def filter_bright_stars(bb):
    vn = []
    for v in bb:
        if not hasattr(v, 'variablestar'): # not registered
            n = v.var_id.replace('/','')
            if n[:3] != 'Var' and not n.isdigit(): # not NSV star
                vn.append(v)
    print(f"{len(vn)} stars to link")
    return vn

def lookup_star(b, vv):
        found = False
        for x in vv:
            if b.var_id == x.printable_name:
                print(f"FOUND {b} = {x}, {type(x)}")
                found = True
                x.bsc_id = b
                x.save()
                return
        if not found:
            print(f"DID NOT FILE {b}")

def get_stars():
    bb = BrightStar.objects.filter(var_id__isnull=False)  # all variable stars
    stars = filter_bright_stars(bb)
    return stars

def constellation_dict():
    d = {}
    for c in Constellation.objects.all():
        d[c.abbreviation] = c.pk
    return d

def lookup_var(s):
    if s in VARDES:
        return VARDES.index(s)
    return None

def go():
    vv = VariableStar.objects.all()
    stars = get_stars()
    for star in stars:
        lookup_star(star, vv)
