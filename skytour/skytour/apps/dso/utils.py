from ..site_parameter.helpers import find_site_parameter
from .vocabs import PRIORITY_VALUES

def create_shown_name(obj, use_con=True):
    """
    This takes the main name, or if there's a Bayer/Flamsteed designation, 
    assemble a string from that.
    """
    things = []
    if obj.catalog.name in ['Bayer', 'Flamsteed']:
            try:
                return "{} {}".format(obj.id_in_catalog, obj.constellation.abbreviation)
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
        k = find_site_parameter('atlas-plate-version-key', 'default', 'string')
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

### MODE PRIORITY STUFF
def priority_color(pri):
    colors = ['#888', '#c6f', '#6cf', '#0f0', '#ff6', '#f66']
    if pri is None:
        return None
    else:
        try:
            return colors[pri]
        except: # bad priority!
            return None
        
def priority_symbol(pri, type='light-circle'):
    if pri is None:
        return None
    if pri < 0 or pri > 5:
        return None
    
    emoji_numbers = [ 
        u"\u0030\uFE0F\u20E3", # 0
        u"\u0031\uFE0F\u20E3", # 1
        u"\u0032\uFE0F\u20E3", # 2
        u"\u0033\uFE0F\u20E3", # 3
        u"\u0034\uFE0F\u20E3", # 4
        u"\u0035\uFE0F\u20E3"  # 5 
    ]
    light_circle_numbers = [
        u"\u24EA", u"\u2460", u"\u2461", u"\u2462", u"\u2463", u"\u2464"
    ]
    dark_circle_numbers = [
        u"\U0001F10C", u"\u278A", u"\u278B", u"\u278C", u"\u278D", u"\u278E"
    ]

    if type == 'emoji':
        return emoji_numbers[pri]
    elif type == 'dark-circle':
        return dark_circle_numbers[pri]
    return light_circle_numbers[pri]

def priority_span(priority):
    if priority is None or priority == 'None':
        return None
    color = priority_color(priority)
    symbol = priority_symbol(priority)
    out = f'<span style="color: {color}">{symbol}</span>'
    return out

def get_priority_value_of_observing_mode(dso, mode):
    this_mode = dso.dsoobservingmode_set.filter(mode=mode).first()
    if this_mode is None:
        return None
    return this_mode.priority

def get_priority_label_of_observing_mode(dso, mode):
    priority = get_priority_value_of_observing_mode(dso, mode)
    if priority is None or priority < 0 or priority > 4:
        return 'Unknown'
    return PRIORITY_VALUES[priority]

def get_priority_span_of_observing_mode(dso, mode):
    if mode is None:
        return None
    priority = get_priority_value_of_observing_mode(dso, mode)
    return priority_span(priority)


def add_dso_to_dsolist(add_dso, dsolist):
    if add_dso is None:
        return "Failed: no DSO"
    if dsolist is None:
        return "Failed: no DSOList"
    if add_dso in dsolist.dso.all():
        return "Failed: DSO already on this list"
    try:
        dsolist.dso.add(add_dso)
        return "Success!"
    except:
        return "Failed: unknown error"
    
def delete_dso_from_dsolist(remove_dso, dsolist):
    if remove_dso is None:
        return "Failed: no DSO"
    if dsolist is None:
        return "Failed: no DSO"
    if remove_dso not in dsolist.dso.all():
        return "Failed: DSO is not in this list"
    try:
        dsolist.dso.remove(remove_dso)
        return "Success!"
    except:
        return "Failed: unknown error"
    
