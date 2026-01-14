from skytour.apps.stars.models import BrightStar, VariableStar
from skytour.apps.utils.models import Constellation
VLETTERS = 'ABCDEFGHIKLMNOPQRSTUVWXYZ' # no Z
LETTERS = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'

def get_letters_list():
    ab = VLETTERS
    ll = [None,]
    for x in ab[ab.index('R'):]: # R through Z
        ll.append(x)
    for x in ab[ab.index('R'):]: # RR through ZZ
        for y in ab[ab.index(x):]: 
            ll.append(x + y)
    for x in ab[ab.index('A'):ab.index('R')]:
        for y in ab[ab.index(x):]: # AA through QZ
            ll.append(x + y)
    return ll

def get_greek_list():
    return [None, 
        'Alp', 'Bet', 'Gam', 'Del', 'Eps', 'Zet', 'Eta', 'The',
        'Iot', 'Kap', 'Lam', 'Mu',  'Nu',  'Xi',  'Omi', 'Pi',
        'Rho', 'Sig', 'Tau', 'Ups', 'Phi', 'Chi', 'Psi', 'Ome'
    ]

def get_majiscules():
    return [None,] + list(LETTERS)

def get_miniscules():
    return [None,] + [x.lower() for x in LETTERS]
    
def get_bsc_vars(stars):
    vv = []
    for star in stars:
        if star.var_id is None:
            continue
        if star.var_id.isnumeric():
            continue
        if '/' in star.var_id:
            continue
        if star.var_id[:3] == 'Var':
            continue
        vv.append(star)
    return vv

def get_constellation_dict():
    d = {}
    cc = Constellation.objects.all()
    for c in cc:
        d[c.abbreviation.upper()] = c.pk
    return d

def deconstruct_variable_name(vstr, debug=False):
    cdict = get_constellation_dict()
    try:
        id, con = vstr.split()
    except:
        print(f"Cannot split {vstr}")
        return None
    con = con.upper()
    cid = f"{cdict[con]:02}"
    #
    vardes = get_letters_list()
    greek = get_greek_list()
    lmaj = get_majiscules()
    lmin = get_miniscules()
    # XX - 
    if id[0] == 'V' and id[1:].isnumeric(): # Vnnn = 335 - 8999
        num = int(id[1:])
        digit = ' '
        return f"{cid}{num:04}"
    if id[-1].isdigit():
        digit = str(id[-1])
        text = id[:-1]
    else:
        text = id
        digit = ' '
    if text in vardes:
        num = vardes.index(text)
    elif text in greek:
        num = greek.index(text) + 9000
    elif text in lmin:
        num = lmin.index(text) + 9100
    elif text in lmaj:
        num = lmaj.index(text) + 9200
    else:
        return None
    # There's a weird error here:
    des = f"{cid}{num:04}{digit}".rstrip()
    if des == '859115':
        des = '859015'  # There is some weird error in either the BSC or the GCVS for this star
    elif des == '690040':
        des = '680596'  # VV Pyx = V0596 Pup (constellation boundary issue?)
    return des

def process():
    bb = BrightStar.objects.all()
    vv = VariableStar.objects.all()
    bv = get_bsc_vars(bb) # 912 items
    errors = []
    success = []
    for b in bv:
        vid = deconstruct_variable_name(b.var_id)
        if not vid:
            err = f"{b.var_id} = {b} returned None"
            errors.append(err)
            continue
        var = vv.filter(id_in_catalog=vid).first()
        if var is None:
            err = f"{vid}: {b} Cannot find {b.var_id}"
            errors.append(err)
            continue
        success.append(f"{vid} = {b} = {var}")
        # link the 1:1
        b.variablestar = var
        var.bsc_id = b
        b.save()
        var.save()
    
    return success, errors





