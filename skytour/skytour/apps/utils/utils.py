from itertools import takewhile

def get_filter_list(request):
    filters = []
    filter_names = ['seen', 'important', 'unseen', 'available', 'imaged', 'unimaged']
    for f in filter_names:
        if request.GET.get(f, False):
            filters.append(f)
    return filters

def filter_dso_test(dso, filters):
    if filters is None:
        return dso
    if 'seen' in filters and dso.observations.count() == 0:
        return None
    if 'important' in filters and dso.priority not in ['High', 'Highest']:
        return None
    if 'unseen' in filters and dso.observations.count() != 0:
        return None
    if 'available' in filters and dso.priority == 'None':
        return None
    if 'imaged' in filters and dso.num_library_images == 0:
        return None
    if 'unimaged' in filters and dso.num_library_images != 0:
        return None
    return dso

def try_int(x):
    try:
        return int(x)
    except:
        foo = "".join(takewhile(str.isdigit, x)) # "55-57" returns 55, pizza returns 0 
        if foo[0].isdigit:
            return int(foo)
        return 0

def original_objects_sort(catalog, primary_dsos, alias_dsos, filters):
    all_objects = []
    for o in primary_dsos:
        if filters is not None and filter_dso_test(o, filters) is None:
            continue
        entry = {}
        entry['in_catalog'] = o.id_in_catalog
        entry['primary_catalog'] = None
        entry['dso'] = o
        all_objects.append(entry)
    for o in alias_dsos:
        if filters is not None and filter_dso_test(o, filters) is None:
            continue
        entry = {}
        entry['primary_catalog'] = o.shown_name
        entry['in_catalog'] = o.aliases.filter(catalog = catalog).first().id_in_catalog
        entry['dso'] = o
        all_objects.append(entry)
    try:
        all_objects_sort = sorted(all_objects, key=lambda d: try_int(d['in_catalog']))
    except:
        all_objects_sort = sorted(all_objects, key=lambda d: str(d['in_catalog']))
    return all_objects_sort

def new_objects_sort(catalog, primary_dsos, alias_dsos, filters):
    digits = 3 if catalog.number_objects is None else len(f"{catalog.number_objects}")
    odict = {}
    all_objects_sort = []
    for o in primary_dsos:
        k = make_id_key(o.id_in_catalog, digits=digits)
        odict[k] = {
            'in_catalog': o.id_in_catalog, 
            'primary_catalog': None, 
            'dso': o,
            'in_field': False, 
            'field_dso': None
        }
    for o in alias_dsos:
        for a in o.aliases.all(): # Because you can have multiple entires amongst the aliases
            if a.catalog == catalog:
                k = make_id_key(a.id_in_catalog, digits=digits)
                if a.alias_in_field == 1:
                    in_field = True
                    field_dso = a.in_field_dso
                else:
                    in_field = False
                    field_dso = ''
                odict[k] = {
                    'in_catalog': a.id_in_catalog, 
                    'primary_catalog': o.shown_name, 
                    'dso': o,
                    'in_field': in_field,
                    'field_dso': field_dso
                }
    for k in sorted(odict.keys()):
        all_objects_sort.append(odict[k])
    return all_objects_sort

def make_id_key(x, digits=6):
    """
    This is a prototype --- need to sort out all the possible insanities,
    prob. with regexes...
    """
    nstr = ''
    other = ''
    out = ''
    ok = True
    for z in x:
        if z.isdigit() and ok:
            nstr += z
        else:
            ok = False
            other += z
    if len(nstr) > 0:
        out = f"{int(nstr):0{digits}d}"
        out += other
        return out
    else:
        return x


