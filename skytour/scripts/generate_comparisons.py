from skytour.apps.dso.models import DSO, DSOInField
from skytour.apps.astro.utils import alt_get_small_sep

def get_id(obj):
    c = "D" if obj._meta.model_name == 'dso' else 'F'
    return f"{c}{obj.pk:05d}"

#### MAGNITUDES
def extract_magnitude(obj):
    KEY_LISTS = {'mag': [('vt', 'V'), ('bt', 'B')],}
    out = []
    metatext = None
    metaval = None
    metalabel = None
    if obj.metadata is not None and 'values' in obj.metadata.keys():
        values = obj.metadata['values']
        for item in KEY_LISTS['mag']:
            (key, label) = item
            if key in values.keys():
                metatext = values[key]['text']
                tval = values[key]['value']
                metaval = tval[0] if type(tval) == list else tval
                metalabel = label
                break
        out = [metatext, metaval, metalabel]
        return out
    return None

def update_magnitude(obj):
    mlist = extract_magnitude(obj)
    if mlist is not None:
        obj.magnitude = mlist[1]
        try:
            obj.save()
        except:
            pass
    return obj

### ANGULAR SIZE
def extract_angular_size(obj):
    out = []
    amajor = None
    aminor = None
    text = None
    logd25_text = None
    logr25_text = None
    if obj.metadata is not None and 'values' in obj.metadata.keys():
        values = obj.metadata['values']
        if 'logd25' in values.keys():
            logd25_text = values['logd25']['text']
            dval = values['logd25']['value']
            logd25_value = dval[0] if type(dval) == list else dval
            amajor = 10.**(logd25_value - 1.) # arcminutes
        if 'logr25' in values.keys():
            logr25_text = values['logr25']['text']
            rval = values['logr25']['value']
            logr25_value = rval[0] if type(rval) == list else rval
            aminor = amajor / (10. ** logr25_value)

        # text string
        if amajor == aminor and amajor is not None:
            text = f"{amajor:.1f}\'"
        else:
            text = f"{amajor:.1f}\' x {aminor:.1f}\'"
        out = [text, amajor, logd25_text, aminor, logr25_text]
        return out
    return None

def update_angular_size(obj):
    alist = extract_angular_size(obj)
    if alist is not None:
        obj.angular_size = alist[0]
        obj.major_axis_size = alist[1]
        obj.minor_axis_size = alist[2]
        try:
            obj.save()
        except:
            pass
    return obj

### SURFACE BRIGHTNESS
def extract_surface_brightness(obj):
    out = []
    bri25_text = None
    bri25_value = None
    brief_text = None
    brief_value = None
    if obj.metadata is not None and 'values' in obj.metadata.keys():
        values = obj.metadata['values']
        if 'bri25' in values.keys():
            bri25_text = values['bri25']['text']
            b25 = values['bri25']['value']
            bri25_value = b25[0] if type(b25) == list else b25
            bri25_value -= 8.89 # convert to SQM
        if 'brief' in values.keys():
            brief_text = values['brief']['text']
            br0 = values['brief']['value']
            brief_value = br0[0] if type(br0) == list else br0
            brief_value -= 8.89
        return [bri25_text, bri25_value, brief_text, brief_value]
    return None

def update_surface_brightness(obj):
    blist = extract_surface_brightness(obj)
    if blist is not None:
        obj.surface_brightness = blist[1]
        try:
            obj.save()
        except:
            pass
    return obj

### ORIENTATION
def extract_orientation(obj):
    out = []
    pa_text = None
    pa_value = None
    if obj.metadata is not None and 'values' in obj.metadata.keys():
        values = obj.metadata['values']
        if 'pa' in values.keys():
            pa_text = values['pa']['text']
            pa = values['pa']['value']
            pa_value = pa[0] if type(pa) == list else pa
        return [pa_text, pa_value]
    return None

def update_orientation(obj):
    olist = extract_orientation(obj)
    if olist is not None:
        obj.orientation_angle(int(olist[1]))
        obj.save()
    return obj

### DISTANCE
def extract_distance(obj):
    """
    only for galaxies?
    """
    out = []
    distmod_text = None
    distmod_value = None
    dist_mly = None
    if obj.metadata is not None and 'values' in obj.metadata.keys():
        values = obj.metadata['values']
        for modtype in ['modbest', 'mod0', 'modz']:
            if modtype in values.keys():
                distmod_text = values[modtype]['text']
                dv = values[modtype]['value']
                distmod_value = dv[0] if type(dv) == list else dv
            x = 1. + distmod_value / 5.
            dist_mly = 10. ** x # parsecs
            dist_mly *= 3.26e-6 # Mly
            return [distmod_text, distmod_value, dist_mly, modtype]
    return None

def update_distance(obj):
    dlist = extract_distance(obj)
    if dlist is not None:
        obj.distance = dlist[2]
        obj.distance_units = 'Mly'
        try:
            obj.save()
        except:
            pass
    return obj

### COORDINATES
def extract_coords(obj, update=False):
    if obj.metadata is not None:
        md = obj.metadata
        if 'ra' in obj.metadata.keys() and 'dec' in obj.metadata.keys():
            mdra = obj.metadata['ra']
            mddec = obj.metadata['dec']
            if mdra is not None and mddec is not None:
                ra_h = int(obj.metadata['ra'][0])
                ra_m = int(obj.metadata['ra'][1])
                ra_s = float(obj.metadata['ra'][2])
                ra_float = float(obj.metadata['ra_float'])
                dec_sign = obj.metadata['dec'][0]
                dec_d = int(obj.metadata['dec'][1])
                dec_m = int(obj.metadata['dec'][2])
                dec_s = float(obj.metadata['dec'][3])
                dec_float = float(obj.metadata['dec_float'])
                return([ra_h, ra_m, ra_s, ra_float, dec_sign, dec_d, dec_m, dec_s, dec_float])
    return None

OVERRIDE_COORDS = {
    'D00624': [ 6, 17, 35.89,  6.29329, '+', 22, 45,  4.0,  22.75111],
    'D00846': [ 6, 16, 36.01,  6.27666, '+', 23, 18, 46.1,  23.31280],
    'D01282': [11, 38, 22.00, 11.63944, '-', 63, 22,  8.3, -63.36896],
    'D00227': [18, 17,  0.  , 18.28333, '-', 18, 29,  0.0, -18.48333],
    'D00257': [20, 16, 46.31, 20.27952, '+', 41, 57, 30.0,  41.95833],
    'D02500': [21, 52, 20.23, 21.87227, '-', 81, 32,  7.4, -81.53538],
    'D00251': [20, 58, 45.47, 20.97929, '+', 43, 57, 35.4,  43.95983],
    'F01184': [ 5,  1, 48.36,  5.03009, '-', 65, 49, 36.1, -65.82668],
    'F01356': [11, 21, 40.44, 11.36123, '+',  2, 57, 47.4,  -2.96316],
    'F01546': [11, 56, 42.90, 11.94524, '+', 32, 11,  8.2,  32.18560],
    'D00089': [ 6,  9, 44.67,  6.16240, '+', 20, 29, 59.5,  20.49985],
    'F00541': [22, 36, 21,92, 22.60608, '+', 34, 32, 45.9,  34.54608]
}
def update_coords(obj, coords, debug=False):
    id = get_id(obj)
    if coords is None:
        print(f"No Coords: {id} = {obj.shown_name:20s} ... skipping")
        return obj
    if id in OVERRIDE_COORDS.keys():
        coords = OVERRIDE_COORDS[id]

    print(f"Updating: {id} = {obj.shown_name:20s} from {obj.ra:.5f} {obj.dec:.5f} to {coords[3]:.5f} {coords[8]:.5f}")
    if coords and len(coords) == 9:
        obj.ra_h = coords[0]
        obj.ra_m = coords[1]
        obj.ra_s = coords[2]
        #obj.ra_float = coords[3]
        obj.dec_sign = coords[4]
        obj.dec_d = coords[5]
        obj.dec_m = coords[6]
        obj.dec_s = coords[7]
        #obj.dec_float = coords[8]
        try:
            if not debug:
                obj.save()
        except:
            pass
    return obj


def generate_mag_list(code='D'):
    out = []
    model = DSO if code == 'D' else DSOInField
    all = model.objects.all()
    for obj in all:
        out.append(extract_magnitude(obj))
    return out

def export_mags():
    dout = generate_mag_list(code='D')
    fout = generate_mag_list(code='F')
    all = dout + fout
    with open('dso_magnitudes.tsv', 'w') as f:
        for obj in all:
            f.write(f"{obj}\n")
    f.close()

def analyze_coords(objset, cap=60):
    out = ""
    max = 0
    n = 0
    for obj in objset:
        clist = extract_coords(obj)
        id = get_id(obj)
        if clist is not None:
            d = alt_get_small_sep(obj.ra_float, obj.dec_float, clist[3], clist[8], unit='arcsec')
            max = max if d < max else d
            if d >= cap:
                out += f"{id}: {obj.shown_name} {obj.object_type}\n"
                out += f"Orig: {obj.ra_h:02d}h {obj.ra_m:02d}m {obj.ra_s:.2f}s  {obj.dec_sign}{obj.dec_d:02d}° {obj.dec_m:02d}\' {obj.dec_s:.1f}\"\n"
                out += f"New:  {clist[0]:02d}h {clist[1]:02d}m {clist[2]:.2f}s  {clist[4]}{clist[5]:02d}° {clist[6]:02d}\' {clist[7]:.1f}\"\n"
                out += f"Difference: {d:.2f}\"\n\n"
                n += 1
    return out, n, max
