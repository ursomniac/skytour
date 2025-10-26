from .models import DSO, DSOInField
from .scrape.leda import process_leda_object
from .scrape.simbad import process_simbad_request

def get_id(obj, model):
    return f"{model}{obj.pk:05d}"

def get_name(obj, code, source):
    name = obj.shown_name
    # Deal with Caldwell objects.
    if obj.catalog.abbreviation == 'C' and code == 'D':
        aa = obj.aliases.all()
        for cat in ['NGC', 'IC']:
            a = aa.filter(catalog__abbreviation=cat).first()
            if a is not None:
                name = f"{a.catalog.abbreviation} {a.id_in_catalog}"
                return name
    elif obj.catalog.abbreviation == 'Ast': # there is no other name for these
        return None
    elif obj.catalog.abbreviation == 'B':
        name = f"Barnard {obj.id_in_catalog}"
    elif obj.catalog.abbreviation == 'Sh2':
        name = f"Sh 2-{obj.id_in_catalog}"
            
    if source == 'simbad':
        if obj.simbad_name is not None:
            name = obj.simbad_name
        elif obj.catalog.abbreviation == 'Cr':
            name = f"Cl Collinder {obj.id_in_catalog}"
        elif obj.catalog.abbreviation == 'Tr':
            name = f"Cl Trumpler {obj.id_in_catalog}"
        elif obj.catalog.abbreviation == 'Mel':
            name = f"Cl Melotte {obj.id_in_catalog}"
    else:
        if obj.hyperleda_name is not None:
            name = obj.hyperleda_name
    return name

def get_metadata_from_source(service, id, name):
    metadata = None
    if service == 'leda':
        metadata = process_leda_object(id, name)
    elif service == 'simbad':
        metadata = process_simbad_request(id, name)
    return metadata

def process_object(obj, code, source, debug=False, verbose=False):
    mymodel = DSO if code == 'D' else DSOInField
    id = get_id(obj, code)
    name = get_name(obj, code, source)
    if name is None:
        return None
    if verbose:
        print(f"Attempting: {id} = {obj.shown_name} using {name}")
    # 2. Scrape service
    metadata = get_metadata_from_source(source, id, name)
    # 3. Store JSON in the appropriate field
    if metadata is None:
        if verbose:
            print(f"{id} = {obj.shown_name} using {name} - no metadata returned.")
        return None
    if source == 'leda':
        obj.metadata = metadata
    else:
        obj.simbad = metadata

    # 4. Save the object
    if debug and verbose:
        print(f"Would be saving to {obj} in {mymodel}")
    if not debug:
        if verbose:
            print(f"Saving metadata to {obj} in {mymodel}")
        obj.save()