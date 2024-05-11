from skytour.apps.dso.models import DSO, DSOInField
from skytour.apps.astro.utils import get_size_from_logd25 as fas, get_distance_from_modulus as unmod, sqs_to_sqm as sqm

def get_dso(pk, model_id): # D00000 or F00000
    model = DSO if model_id == 'D' else DSOInField
    obj = model.objects.filter(pk=pk).first()
    return obj # will be None if doesn't exist

def make_table(clist):
    for row in clist:
        print(row)

def compare(label, dso, leda):
    return f"{label:20s}: {str(dso):20s} | {str(leda):20s}"

def get_ra(vv):
    if 'ra' in vv.keys():
        return str(vv['ra'])
    return ""

def get_dec(vv):
    if 'dec' in vv.keys():
        return str(vv['dec'])
    return ""

def get_single_value(raw):
    return raw if type(raw) != list else raw[0]

def get_leda_size(vv):
    if 'logd25' in vv.keys():
        v0 = get_single_value(vv['logd25']['value'])
    if 'logr25' in vv.keys():
        v1 = get_single_value(vv['logr25']['value'])
        amajor, aminor = fas(v0, ratio=v1, raw=True)
    else:
        amajor, aminor = fas(v0, raw=True)
    atext = f"{amajor:.1f}\'"
    if amajor != aminor:
        atext += f" x {aminor:.1f}\' "
    return str([atext, amajor, aminor])

def get_surface_brightness(vv):
    if 'bri25' in vv.keys():
        sqs = get_single_value(vv['bri25']['value'])
        return sqm(sqs)
    return ""

def get_object_type(vv):
    return vv['objtype']['text'] if 'objtype' in vv.keys() else None

def get_morphology(vv):
    tt = []
    if 'type' in vv.keys():
        tt.append(vv['type']['text'])
    if 't' in vv.keys():
        tt.append(vv['t']['text'])
    return ' '.join(tt)

def get_magnitude(vals):
    if 'vt' in vals.keys():
        return vals['vt']['text']
    elif 'bt' in vals.keys():
        return vals['bt']['text'] + ' B'
    return ""

def get_distance(vv):
    if 'modbest' in vv.keys():
        dmod = get_single_value(vv['modbest']['value'])
        return f"{unmod(dmod):.2f} Mly"
    return ""

def analyze_dso(dso):
    md = dso.metadata
    if md is None:
        return None
    vals = md['values']
    if vals is None:
        return None
    
    clist = []
    # 1. Coordinates
    dso_ra = str((dso.ra_h, dso.ra_m, dso.ra_s))
    leda_ra = get_ra(md)
    clist.append(compare('RA', dso_ra, leda_ra))
    dso_dec = str((dso.dec_sign, dso.dec_d, dso.dec_m, dso.dec_s))
    leda_dec = get_dec(md)
    clist.append(compare('Dec', dso_dec, leda_dec))

    # 2. Object Type/Morphology
    leda_type = get_object_type(vals)
    clist.append(compare('Type', dso.object_type, leda_type))
    leda_morph = get_morphology(vals)
    clist.append(compare('Morph', dso.morphological_type, leda_morph))
    
    # 3. Magnitude [vt, bt, it]
    leda_mag = get_magnitude(vals)
    clist.append(compare('Mag', dso.magnitude, leda_mag))

    # 4. Angular Size [logd25/logr25]
    dso_size = (dso.angular_size, dso.major_axis_size, dso.minor_axis_size)
    leda_size = get_leda_size(vals)
    clist.append(compare('Size.', dso_size, leda_size))

    # 5. Surface brightness [bri25, brief]
    leda_sb = get_surface_brightness(vals)
    clist.append(compare('Surf. Br.', dso.surface_brightness, leda_sb))

    # 6. Distance [modbest, mod0]
    dso_dist = f"{dso.distance} {dso.distance_units}"
    leda_dist = get_distance(vals)
    clist.append(compare('Distance: ', dso_dist, leda_dist))

    return clist
                 

def is_galaxy(dso):
    return dso.object_type.slug in ['barred-spiral', 'dwarf-galaxy', 'galaxy--elliptical', 'irregular-galaxy',
        'galaxy--lenticular', 'seyfert-galaxy', 'galaxy--spiral', 'galaxy--unclassified']

def get_leda_text_value(md, key):
    if md is None:
        return ""
    return md[key]['text'] if key in md.keys() else ""

def get_leda_morph_code_value(md):
    if md is None:
        return ""
    if 't' in md.keys():
        v = md['t']['value']
        return str(v) if type(v) != list else str(v[0])
    return ""

def find_all_morphologies(objs, model, lines):
    for d in objs:
        if not is_galaxy(d):
            continue
        id = f"{model}{d.pk:05d}"
        old_morph = d.morphological_type or ""
        md = d.metadata['values']
        leda_objtype = get_leda_text_value(md, 'objtype')
        leda_code = get_leda_text_value(md, 't')
        leda_code_value = get_leda_morph_code_value(md)
        leda_type = get_leda_text_value(md, 'type')
        leda_barred = get_leda_text_value(md, 'bar')
        leda_ringed = get_leda_text_value(md, 'ring')
        out = [id, d.shown_name, d.object_type.slug, old_morph, leda_objtype, leda_code,\
               leda_code_value, leda_type, leda_barred, leda_ringed]
        line = '\t'.join(out)
        lines.append(line)
    return lines

def run_all_galaxies():
    lines = []
    dd = DSO.objects.all()
    lines = find_all_morphologies(dd, 'D', lines)
    ff = DSOInField.objects.all()
    lines = find_all_morphologies(ff, 'F', lines)
    with open('galaxies_all.txt', 'w') as f:
        for line in lines:
            f.write(f"{line}\n")
    f.close()