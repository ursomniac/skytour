import re

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

