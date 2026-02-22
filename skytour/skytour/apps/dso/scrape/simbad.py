from astroquery.simbad import Simbad
from .utils import *

def setup_simbad():
    csim = Simbad()
    csim.reset_votable_fields()
    # Deprecations > V0.4.8
    #csim.add_votable_fields('dim', 'distance', 'jp11', 'flux(V)', 'flux(B)', 'morphtype', 'otype')
    csim.add_votable_fields('dim', 'mesdistance', 'flux', 'V', 'B', 'morphtype', 'otype')
    return csim

def process_simbad_object(obj):
    data = obj.columns.items()
    d = {}
    for k, v in data:
        value = v.tolist()[0]
        try:
            units = v.unit.to_string()
        except:
            units = None
        d[k] = (value, units)
    return d

def simbad_make_request(name, csim):
    simobj = csim.query_object(name)
    return simobj

def simbad_parse_coords_old(objdict):
    if 'RA' not in objdict.keys() or 'DEC' not in objdict.keys():
        return None, None
    try:
        ra = objdict['RA'][0].split(' ')
        ra_h = ra[0]
        ra_m = '0' if len(ra) < 2 else ra[1]
        ra_s = '0' if len(ra) < 3 else ra[2]
        tra = (ra_h, ra_m, ra_s)
        dec = objdict['DEC'][0].split()
        sign = dec[0][0] if dec[0][0] in '+-' else '+'
        start = 1 if dec[0][0] in '+-' else 0
        dec_d = dec[0][start:]
        dec_m = '0' if len(dec) < 2 else dec[1]
        dec_s = '0' if len(dec) < 3 else dec[2]
        tdec = (sign, dec_d, dec_m, dec_s)
        return tra, tdec
    except:
        return None, None
    
def simbad_parse_coords(objdict):
    if 'ra' not in objdict.keys() or 'dec' not in objdict.keys():
        return None, None
    try:
        ra = objdict['ra'][0] / 15.
        dec = objdict['dec'][0]
        return ra, dec
    except:
        return None, None

def normalize_simbad(vals):
    v = {}

    # angular size and orientation
    SIZE_CONV = {'arcsec': 60., 'degrees': 1/60., 'mas': 60.e3}
    amajor = None
    aminor = None
    if 'GALDIM_MAJAXIS' in vals.keys():
        amajor = vals['GALDIM_MAJAXIS'][0]
        amaju = vals['GALDIM_MAJAXIS'][1]
        if amaju != 'arcmin' and amaju in SIZE_CONV.keys():
            amajor *= SIZE_CONV[amaju]
            amaju = 'arcmin'
        if amajor is not None:
            v['amajor'] = dict(value=norm_float(amajor, 3), units=amaju)
    if 'GALDIM_MINAXIS' in vals.keys():
        aminor = vals['GALDIM_MINAXIS'][0]
        aminu = vals['GALDIM_MINAXIS'][1]
        if aminu != 'arcmin' and aminu in SIZE_CONV.keys():
            aminor *= SIZE_CONV[aminu]
            aminu = 'arcmin'
        if aminor is not None:
            v['aminor'] = dict(value=norm_float(aminor, 3), units=aminu)
    if amajor is not None and aminor is not None:
        if amajor == aminor:
            v['angsize'] = f"{amajor:.1f}\'"
        else:
            try:
                v['angsize'] = f"{amajor:.1f}\' x {aminor:.1f}\'"
            except:
                print(f"Problem with {amajor} and {aminor}")
    if 'GALDIM_ANGLE' in vals.keys():
        orientation = vals['GALDIM_ANGLE'][0]
        units = vals['GALDIM_ANGLE'][1]
        if orientation is not None:
            v['orientation'] = dict(value=orientation, units=units)

    # magnitude
    for k in ['FLUX_V', 'FLUX_B']:
        if k in vals.keys():
            if vals[k] is not None:
                mag = vals[k][0]
                system = k[-1]
                if mag is not None:
                    v['magnitude'] = dict(value=norm_float(mag), system=system)
                    break

    # distance
    dist = None if 'Distance_distance' not in vals.keys() else vals['Distance_distance'][0]
    units = None if 'Distance_unit' not in vals.keys() else vals['Distance_unit'][0]
    dist, units = norm_distance(dist, units)
    if dist is not None:
        v['distance'] = dict(value=dist, units=units)
    return v

def norm_distance(x, units):
    # OK - there's a bug here:
    #   if x < 1 and units is Mly, then you'll get back
    fix_units = {'Mpc': 'kpc', 'Mly': 'kly', 'kpc': 'pc', 'kly': 'ly'}
    if x is None:
        return x, units
    if x <= 1. and units in fix_units.keys():
        x *= 1000.
        units = fix_units[units]

    if units == 'Mpc':
        return norm_float(x * 3.26, 1), 'Mly'
    if units == 'Mly':
        return norm_float(x, 1), 'Mly'
    if units == 'kpc':
        return norm_float(x * 3.26, 2), 'kly'
    if units == 'pc':
        return norm_float(x * 3.26, 2), 'ly'
    if units == 'ly':
        return norm_float(x, 2), 'ly'
    else:
        return x, units

def norm_float(x, prec=2):
    s = f"{x:.{prec}f}"
    return float(s)

def process_simbad_request(id, name, debug=False):
    simbad = setup_simbad()
    if debug:
        print("SIMBAD: ", simbad)
    req = simbad_make_request(name, simbad)
    if debug:
        print("REQ: ", req)
    if req is None:
        if debug:
            print(f"{id}: Cannot find {name} in SIMBAD.")
        print("GOT HERE: ", req)
        return None
    try:
        objdict = process_simbad_object(req)
    except:
        print(f"ERROR - REQ: {req}")
        return None
    if debug:
        print("OBJDICT: ", objdict)
        print("KEYS: ", objdict.keys())
    #if 'MAIN_ID' in objdict.keys():
    #    if type(objdict['MAIN_ID']) == tuple:
    #        if objdict['MAIN_ID'][1] is None: # nothing came back!
    #            return None
    d = {}
    d['ra_float'], d['dec_float'] = simbad_parse_coords(objdict)
    if d['ra_float'] is None and d['dec_float'] is None:
        return None
    #d['ra_float'] = convert_ra(d['ra'])
    #d['dec_float'] = convert_dec(d['dec'])
    d['raw_values'] = objdict
    d['values'] = normalize_simbad(objdict)
    raw_aliases = simbad.query_objectids(name)
    #grab = [a[0].decode('utf-8') for a in raw_aliases.as_array().tolist()]
    grab = [a[0] for a in raw_aliases.as_array().tolist()]
    d['aliases'] = [' '.join(x.split()) for x in grab]
    return d
    