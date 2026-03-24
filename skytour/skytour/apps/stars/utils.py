import math, re
from .vocabs import VARDES, BAYER_INDEX

def create_star_name(obj):
    """
    Generate a label from it's Bayer/Flamsteed designation.
    """
    if obj.bayer:
        return "{} {}".format(obj.bayer, obj.constellation.abbr_case)
    elif obj.flamsteed:
        return "{} {}".format(obj.flamsteed, obj.constellation.abbr_case)
    return None

GREEK = {
    'Alp': '\\alpha', 'Bet': '\\beta', 'Gam': '\\gamma', 'Del': '\\delta',
    'Eps': '\\epsilon', 'Eta': '\\eta', 'Zet': '\\zeta', 'The': '\\theta',
    'Iot': '\\iota', 'Kap': '\\kappa', 'Lam': '\\lambda', 'Mu': '\\mu', 
    'Nu': '\\nu', 'Omi': 'o', 'Xi': '\\xi', 'Pi': '\\pi', 
    'Rho': '\\rho', 'Sig': '\\sigma', 'Tau': '\\tau', 'Ups': '\\upsilon', 
    'Chi': '\\chi', 'Phi': '\\phi', 'Psi': '\\psi', 'Ome': '\\omega'
}

def parse_designation(str):
    """
    E.g. Bet, Bet2, etc.
    Make the number a superscript.
    Return the LaTeX representation.
    """
    x = None
    match = re.match(r"([A-z]+)([1-9]*)", str)
    if match:
        items = match.groups()
        if items[0] in GREEK.keys():
            x = GREEK[items[0]]
        if items[1] and items[1] != '':
            x += "^{}".format(items[1])
        return "${}$".format(x)
    else:
        return str

def order_bright_stars(stars):
    """
    This is slow but the size of the querysets aren't large
    """
    return sorted(stars, key=lambda t: t.name_sort_key)

def parse_other_bayer(x, p=2):
    upper = ' ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    lower = ' abcdefghijklmnopqrstuvwxyz'
    idx = number = None
    x = 'L 1' if x == 'L1' else x
    x = 'X' if x == 'X_' else x
    if x[:3] in ['Omi', 'Ups']:
        return None
    # x or x 1?
    if x[-1].isdigit():
        letter, number = x.split()
    else:
        letter = x[0]
        number = '0'
    if letter in upper:
        idx = upper.index(letter) + 1000
    elif letter in lower:
        idx = lower.index(letter) + 2000
    if idx and number:
        return f"{p}{idx:05d}{int(number):03d}"
    return None

def parse_variable_name(v, p=4):
    x = v.split()[0]
    if x in VARDES:
        number = VARDES.index(x)
    elif x[0] == 'V' and x[1:].isnumeric():
        number = int(x[1:])
    else:
        return None
    return f"{p}{int(number):08d}"

def get_bright_star_sort_key(star):
    """
    Return a coded key such that:
        1. Stars with Greek letters come first in Greek order
        2. Stars with superscripts for a given Greek letter are ordered
        3. Stars with a Flamsteed number and no Greek letter are next
        4. Stars with HD numbers come last
    """
    out = None
    if star.bayer:
        p = 1
        if star.bayer[-1].isdigit(): # there's a number
            x = star.bayer[:-1].rstrip()
            d = star.bayer[-1]
            num = int(d) if d.isdigit() else 0
        else: # no number
            x = star.bayer
            num = 0
        if x in BAYER_INDEX:
            grk = BAYER_INDEX.index(x)
            out = f"{p}{grk:05d}{num:03d}"
    if out is None and star.flamsteed:
        p = 3
        num = star.flamsteed
        if num.isdigit():
            out = f"{p}{int(num):08d}"
    if out is None and star.var_id:
        # p = 4
        out = parse_variable_name(star.var_id)
    if out is None and star.other_bayer:
        # p = 5
        out = parse_other_bayer(star.other_bayer)
    if out is None:
        p = 6
        hd = star.hd_id
        out = f"{p}{hd:08d}"
    return out

def get_default_notes_panel(s):
    x = None # default
    x = 'bsc' if s.texts.notes_as_html else x # override
    x = 'wiki' if s.has_wiki == 'WIKI' else x # override again
    x = 'annals' if s.has_annals else x # override again (see how this works)?
    return x

def handle_formatting(n):
    SWAPS = [
        ('_sun', '<sub>&#9737;</sub> '), ('_Sun', '<sub>&#9737;</sub>' ),
        ('_Earth', '🜨'), ('_E', '🜨'), ('_earth', '🜨'),
        ('_Jup', '<sub>&#9795;</sub>'), ('_J', '<sub>&#9795;</sub>'), 
        ('_gal', '<sub>gal</sub>'),
        ('^1', '<sup>1</sup>'), ('^2', '<sup>2</sup>'), ('^3', '<sup>3</sup>'),
        ('^4', '<sup>4</sup>'), ('^5', '<sup>5</sup>'), ('^6', '<sup>6</sup>'),
        ('^7', '<sup>7</sup>'), ('^8', '<sup>8</sup>'), ('^9', '<sup>9</sup>'),
        ('_0', '<sub>0</sub>'), ('_*', '<sub>*</sub>'),
        ('vsini', '<i>v</i> sin <i>i</i>'), ('P_rot', '<i>P</i><sub>rot</sub>'),
        ('v_equ', '<i>v</i><sub>equ</sub>'), ('P_cyc', '<i>P</i><sub>cyc</sub>'),
        ('v_eq', '<i>v</i><sub>equ</sub>'), ('P_orb', '<i>P</i><sub>orb</sub>'),
        ('v_rot', '<i>v</i><sub>rot</sub>'),
        ('>~', '≳'), ('<~', '≲'),
    ]
    for x in SWAPS:
        n = n.replace(x[0], x[1])
    return n

def gridify(x, nc, blank=None):
    nr = math.ceil(len(x)/nc)
    y = [blank] * nr * nc
    for i in range(nc):
        for j in range(nr):
            xindex = i * nr + j
            yindex = j * nc + i
            if xindex < len(x):
                y[yindex] = x[xindex]
    return y

def handle_parameters(orig, cols=1, blank='', label_style=None):
    """
    Get/Format Additional Metadata text
    """
    out = None
    if orig is not None and orig.strip() != '':
        interim = []
        first = orig.split(';')
        for item in first:
            if item is None or item.strip() == '':
                continue
            if ':' in item:
                (label, value) = item.split(':')
            else: # this shouldn't happen but...
                label = item
                value = ''
            t = tuple((label.strip(), value.strip()))
            interim.append(t)
        second = sorted(interim, key=lambda x: x[0])
        out = []
        for item in second:
            label = handle_formatting(item[0])
            param = handle_formatting(item[1])
            if label_style:
                label = f'<span class="{label_style}">{label}</span>'
            out.append(f"{label}: {param}")

    # Deal with columns:
    if cols > 1 and out is not None and len(out) > 0:
        out = gridify(out, cols, blank=blank)
    return out

def get_bsc_uvw_params(star, debug=True):
    d = {}
    try:
        v = star.metadata.metadata['values']
        if type(v) == list:
            v = v[0]
    except:
        v = None

    ra = star.ra_float * 15.
    dec = star.dec_float
    if debug:
        print(f"\tRA: {ra}\n\tDec: {dec}")
    # PM
    try:
        ra_pm = v['proper_motion']['ra']['value']
        dec_pm = v['proper_motion']['dec']['value']
        if debug:
            print(f"\tPM RA: {ra_pm} Simbad\n\tPM Dec: {dec_pm}")
    except Exception:
        try:
            ra_pm = star.pm_ra / 100.
            dec_pm = star.pm_dec / 100.
            if debug:
                print(f"\tPM RA: {ra_pm} BSC\n\tPM Dec: {dec_pm}")
        except:
            return None
    # Distance
    try:
        distance = v['distance']['pc']['value']
        if debug:
            print(f"\tDist: {distance} SIMBAD")
    except Exception:
        try:
            distance = d.distance_pc
            if debug:
                print(f"\tDist: {distance} BSC")
        except:
            return None
    # RV
    try:
        rv = v['radial_velocity']['value']
        if debug:
            print(f"\tRV: {rv} SIMBAD")
    except Exception:
        try:
            rv = star.radial_velocity
            print(f"\tRV: {rv} BSC")
        except:
            return None
        
    if any(x is None for x in [ra, dec, ra_pm, dec_pm, distance, rv]):
        return None
    return (ra, dec, ra_pm, dec_pm, distance, rv)

