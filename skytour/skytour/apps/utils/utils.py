from itertools import takewhile

def filter_catalog(request, dso_list, cookie):
    observed = request.GET.get('observed', None)
    available = request.GET.get('available', None) == 'on'
    imaged = request.GET.get('imaged', None)
    constr = request.GET.get('constellation', None)
    if constr is None or constr == '':
        con_list = None
    else:
        con_list = [x.lower().strip() for x in constr.split(',')]
    # AND all the filters
    if observed and observed != '':
        new = []
        for d in dso_list:
            o = d['dso']
            if observed == 'yes' and o.observations.count() > 0:
                new.append(d)
            elif observed == 'no' and o.observations.count() == 0:
                new.append(d)
        dso_list = new
    if imaged and imaged != '':
        new = []
        for d in dso_list:
            o = d['dso']
            if imaged == 'yes' and o.num_library_images > 0:
                new.append(d)
            elif imaged == 'no' and o.num_library_images == 0:
                new.append(d)
        dso_list = new
    if available:
        try:
            d0, d1 = cookie['dec_range']
            new = []
            for d in dso_list:
                o = d['dso']
                if o.dec >= d0 and o.dec <= d1:
                    new.append(d)
            dso_list = new
        except:
            print("Error getting dec")
    if con_list is not None:
        new = []
        for d in dso_list:
            o = d['dso']
            if o.constellation.abbreviation.lower() in con_list:
                new.append(d)
        dso_list = new
        if len(new) == 0:
            print("CONSTELLATION FAILED")
    return dso_list

def try_int(x):
    try:
        return int(x)
    except:
        foo = "".join(takewhile(str.isdigit, x)) # "55-57" returns 55, pizza returns 0 
        if foo[0].isdigit:
            return int(foo)
        return 0

# DEPRECATED - keep for now to see if we need anything from here...
def new_objects_sort(catalog, primary_dsos, alias_dsos, field_dsos):
    odict = {}
    all_objects_sort = []
    for o in primary_dsos:
        k = o.id_as_digits
        odict[k] = {
            'as_digits': k,
            'in_catalog': o.id_in_catalog, 
            'primary_catalog': None, 
            'dso': o,
            'in_field': False, 
            'field_dso': None
        }
    for o in field_dsos:
        k = o.id_as_digits
        odict[k] = {
            'as_digits': k,
            'in_catalog': o.id_in_catalog,
            'primary_catalog': None,
            'dso': o.parent_dso,
            'in_field': True,
            'field_dso': o
        }
    for o in alias_dsos:
        for a in o.aliases.all(): # Because you can have multiple entries amongst the aliases
            if a.catalog == catalog:
                k = o.id_as_digits
                if a.alias_in_field == 1:
                    in_field = True
                    field_dso = a.in_field_dso
                else:
                    in_field = False
                    field_dso = ''
                odict[k] = {
                    'as_digits': k,
                    'in_catalog': a.id_in_catalog, 
                    'primary_catalog': o.shown_name, 
                    'dso': o,
                    'in_field': in_field,
                    'field_dso': field_dso
                }
    for k in sorted(odict.keys()):
        all_objects_sort.append(odict[k])
    return all_objects_sort


