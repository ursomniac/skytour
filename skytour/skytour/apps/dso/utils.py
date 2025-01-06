from ..site_parameter.helpers import find_site_parameter

def create_shown_name(obj, use_con=True):
    """
    This takes the main name, or if there's a Bayer/Flamsteed designation, 
    assemble a string from that.
    """
    things = []
    if obj.catalog.name in ['Bayer', 'Flamsteed']:
            try:
                return "{} {}".format(obj.id_in_catalog, obj.object.constellation.abbreviation)
            except:
                pass
    elif obj.catalog.name == 'Sharpless':
        return f"{obj.catalog.abbreviation}-{obj.id_in_catalog}"
    elif obj.catalog.name == 'Var':
        try:
            return f"{obj.id_in_catalog} {obj.constellation.abbreviation}"
        except:
            pass
    elif obj.catalog.name == '(other)':
        things.append(obj.id_in_catalog)
        if use_con:
            things.append(obj.constellation.abbreviation)
    else:
        if obj.catalog.use_abbr:
            things.append(obj.catalog.abbreviation)
            things.append(obj.id_in_catalog)
        else:
            things.append(obj.id_in_catalog)
            try:
                things.append(obj.constellation.abbreviation)
            except:
                pass
    return ' '.join(things)

def select_atlas_plate(plates, context):
    """
    If the session cookie is set, use that to determine which atlas plate to show.
    If not, then use the 'atlas-version-key' as the default.
    Final back up is 'default'
    """
    k = ''
    reversed = True
    shapes = True
    if 'color_scheme' in context.keys():
        reversed = context['color_scheme'] == 'dark'
    if 'atlas_dso_marker' in context.keys():
        shapes = context['atlas_dso_marker'] == 'shapes'
    
    if shapes:
        k += 'shapes'
    if reversed:
        k += 'reversed'
    if k == '':
        k = find_site_parameter('atlas-plate-version-key', 'default', 'char')
    return plates[k]

def select_other_atlas_plates(plate_list, primary):
    plates = []
    k = 'shapes' if primary.shapes else ''
    k += 'reversed' if primary.reversed else ''
    for key in plate_list.keys():
        if key != k:
            plates.append(plate_list[key])
    return plates

def get_hyperleda_value(obj, key):
    if obj.metadata is None or 'values' not in obj.metadata.keys():
        return None
    vals = obj.metadata['values']
    if key in vals.keys():
        return vals[key]
    return None

def get_simbad_value(obj, key):    
    if obj.simbad is None or 'values' not in obj.simbad.keys():
        return None
    vals = obj.simbad['values']
    if key in vals.keys():
        return vals[key]
    return None
