from skytour.apps.dso.models import DSO, DSOInField, DSOAlias, DSOInFieldAlias
from skytour.apps.utils.models import Catalog

def create_update_list(dsos, catalog, show_all=False):
    update_list = []
    for d in dsos:
        if d.simbad is None or d.simbad['aliases'] is None:
            continue
        aa = d.simbad['aliases']
        for a in aa:
            z = a
            alias_catalog = a.split(' ')[0]
            alias_id = ' '.join(a.split(' ')[1:])

            if alias_catalog in ['LBN', 'C']:
                if '+' in alias_id or '-' in alias_id:
                    continue

            if catalog.abbreviation == 'PGC' and alias_catalog == 'LEDA':
                alias_catalog = 'PGC'
                a = f"PGC {alias_id}"

            if catalog.abbreviation == alias_catalog:
                # But not itself!
                if d.catalog == catalog and d.id_in_catalog == alias_id:
                    print(f"I found myself: {d} = {a}")
                else:
                    entry = (d, a)
                    update_list.append(entry)
            else:
                if show_all:
                    print(f"Not {catalog.abbreviation} {alias_catalog} {z}")
    return update_list

def update_entry(update_entry, alias_catalog, update=False):
    dso, alias = update_entry # deconstruct tuple
    my_model = dso._meta.model_name
    id_in_cat = ' '.join(alias.split(' ')[1:])
    aliases = dso.aliases.all()
    # check to see if we have this one already
    have = aliases.filter(catalog=alias_catalog, id_in_catalog=id_in_cat).first()
    if have is not None:
        print(f"Found existing {have} = {alias} for {dso}")
        return 'exists'
    new = DSOAlias() if my_model == 'dso' else DSOInFieldAlias()
    new.catalog = alias_catalog
    new.id_in_catalog = id_in_cat
    new.object = dso
    if not update:
        print(f"Would create {alias} for {dso}")
        return 'created'
    else:
        try:
            new.save()
            return 'created'
        except:
            print(f"Error saving {new}:")
            print(f"\tDSO: {dso}")
            return 'error'


def run_dso_list(catalog_object, dso_type='d', dsos=None):
    if dsos is None:
        dsos = DSO.objects.all() if dso_type == 'd' else DSOInField.objects.all()
    updates = create_update_list(dsos, catalog_object)
    return updates

def get_catalog(abbr):
    catalog = Catalog.objects.filter(abbreviation=abbr).first()
    if catalog is None:
        print(f"Cannot find {abbr} catalog!")
    return catalog

def run_catalog(abbr, dso_type, dsos=None, update=False):
    results = {}
    catalog = get_catalog(abbr)
    if catalog is None:
        return None
    updates = run_dso_list(catalog, dso_type, dsos=dsos)
    for u in updates:
        flag = update_entry(u, catalog, update=update)
        if flag in results.keys():
            results[flag] += 1
        else:
            results[flag] = 1
    print(f"{len(updates)} to run")
    print(f"RESULTS: {results}")