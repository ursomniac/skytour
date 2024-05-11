import json
import re
import requests
from lxml import html

from skytour.apps.astro.utils import get_distance_from_modulus, get_size_from_logd25
from .utils import *

def leda_make_request(name):
    tag = name.replace(' ', '%20')
    endpoint = f"http://atlas.obs-hp.fr/hyperleda/ledacat.cgi?o={tag}"
    return requests.get(endpoint)

def get_obj_list(model):
    objlist = []
    allobj = model.objects.all()
    for obj in allobj:
        if obj.metadata is None or obj.metadata['ra_float'] is None:
            objlist.append(obj)
    return objlist

def leda_get_coordinate_table(tables):
    for i in range(len(tables)):
        t = tables[i]
        c = t.text_content().replace('\n', ' ')
        if 'J2000' in c and 'Alternate' not in c:
            return t
    return None
    
def leda_get_coordinates(tables):
    table = leda_get_coordinate_table(tables)
    if table is None:
        return None, None
    for tr in table.getchildren(): # should be tr's
        if tr.tag != 'tr':
            continue
        tds = [x.text_content() for x in tr.getchildren()]
        if tds[0] == 'J2000':
            value = tds[1]
            if value[0] == 'J':
                ra = (value[1:3], value[3:5], value[5:10])
                dec = (value[10], value[11:13],value[13:15], value[15:])

                return ra, dec
        return None, None

def leda_get_values_table(tables):
    for i in range(len(tables)):
        trs = tables[i].getchildren()
        if 'Parameter' in trs[0].text_content():
            return tables[i]
    return None

def leda_get_values(tables):
    table = leda_get_values_table(tables)
    if table is None:
        return None
    d = {}
    trs = table.getchildren()[1:] # skip headers
    for tr in trs:
        tds = [x.text_content() for x in tr.getchildren()]
        key = tds[0]
        d[key] = dict(
            text = ' '.join(tds[1].split()),
            value = leda_process_value(tds[1]),
            unit = tds[2],
            description = tds[3]
        )
    return d

def leda_process_value(val):
    if re.search('[a-zA-Z]', val):
        return val
    # Should be number or x ± y
    c = val.replace(' ','')
    if '±' in c:
        try:
            v, e = c.split('±')[:2]
            vv = float(v) if '.' in v else int(v)
            ee = float(e) if '.' in e else int(e)
            return (vv, ee)
        except:
            return c
    try:
        cc = float(c)
        return cc
    except:
        return c

def leda_get_aliases(tables):
    table = None
    for i in range(len(tables)):
        full_content = tables[i].text_content()
        if 'Alternate name' in full_content:
            table = tables[i] # we want the last one
    if table is not None:
        aliases = []
        try:
            header = table.getchildren()[0].getchildren()[1].text_content()
            if header == 'Alternate names': # we Win!
                subtable = table.getchildren()[1].getchildren()[1].getchildren()[0].getchildren()[0]
                strs = [x for x in subtable.getchildren()]
                for str in strs:
                    stds = [x for x in str.getchildren()]
                    for std in stds:
                        aliases.append(std.text_content())
            return aliases
        except:
            pass
    return None

def process_leda_metadata(md):
    d = {}
    # magnitude
    for k in ['vt', 'bt']:
        system = 'V' if k == 'vt' else 'B'
        if k in md.keys():
            raw = md[k]['value']
            mag = raw if type(raw) not in (list, tuple) else raw[0]
            d['magnitude'] = dict(value=mag, system=system)
            break

    # surface brightness
    if 'bri25' in md.keys():
        raw = md['bri25']['value']
        sqs = raw if type(raw) not in (list, tuple) else raw[0]
        d['surface_brightness'] = dict(value = sqs - 8.89, units='sqm')

    # angular size and orientation
    amajor = None
    aminor = None
    orientation = None
    d25 = None
    ratio = None
    if 'logd25' in md.keys():
        raw = md['logd25']['value']
        d25 = raw if type(raw) not in (list, tuple) else raw[0]
    if 'logr25' in md.keys():
        raw = md['logr25']['value']
        ratio = raw if type(raw) not in (list, tuple) else raw[0]
    if d25 is not None:
        if ratio is None:
            ratio = 0.
        amajor, aminor = get_size_from_logd25(d25, ratio, raw=True)
        if amajor == aminor:
            angsize = f"{amajor:.1f}\'"
        else:
            angsize = f"{amajor:.1f}\' x {aminor:.1f}\'"
        d['amajor'] = dict(value=amajor, units='arcmin')
        d['aminor'] = dict(value=aminor, units='arcmin')
        d['angsize'] = angsize
    if 'pa' in md.keys():
        raw = float(f"{md['pa']['value']:.0f}") # stupid python rounding
        d['orientation'] = dict(value=raw, units='deg')
    
    # distance
    for k in ['modbest', 'mod0', 'modz']:
        if k in md.keys():
            raw = md[k]['value']
            mod = raw if type(raw) not in (list, tuple) else raw[0]
            d['distance'] = dict(value = get_distance_from_modulus(mod), units='Mly', method=k)
            break
    return d

def scrape_leda(content, name):
    tree = html.fromstring(content)
    tables = tree.xpath('//table')
    ra, dec = leda_get_coordinates(tables)
    if ra is None and dec is None:
        return None
    raw_values = leda_get_values(tables)
    if raw_values is not None:
        values = process_leda_metadata(raw_values)

    aliases = leda_get_aliases(tables)
    d = dict(
        name = name,
        ra = ra,
        ra_float = convert_ra(ra),
        dec = dec,
        dec_float = convert_dec(dec),
        values = values,
        aliases = aliases,
        raw_values = raw_values
    )
    return d

def leda_process_value(val):
    if re.search('[a-zA-Z]', val):
        return val
    # Should be number or x ± y
    c = val.replace(' ','')
    if '±' in c:
        try:
            v, e = c.split('±')[:2]
            vv = float(v) if '.' in v else int(v)
            ee = float(e) if '.' in e else int(e)
            return (vv, ee)
        except:
            return c
    try:
        cc = float(c)
        return cc
    except:
        return c
    
def process_leda_object(id, name, debug=False):
    request = leda_make_request(name)
    if request.status_code != 200:
        if debug:
            print(f"Cannot look up {id} = {name} in Leda.")
        return None
    d = scrape_leda(request.content, name)
    return d