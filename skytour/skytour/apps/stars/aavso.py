import requests, json
from ..utils.models import Constellation
from .vocabs import BAYER_INDEX

def make_request(name, fov=60., maglimit=14.5, north="up", east="left"):
    root = 'https://app.aavso.org/vsp/api/chart/?'
    orient = f"&north={north}&east={east}"
    format = "&format=json"
    # Handle disambiguation between "Mu" and 'MU' (ditto Nu)
    if name[:3] == 'Mu ':
        name = 'mu. ' + name[3:]
    if name[:3] == 'Nu ':
        name = 'nu. ' + name[3:]
    qs = f"star={name.replace(' ','+')}&fov={fov}&maglimit={maglimit}"

    r = requests.get(root + qs + orient + format)    
    return r

def get_finder_chart(name, url, path='aavso_finder_chart/'):
    r = requests.get(url)
    if r.status_code != 200:
        print(f"ERROR retrieving {url} - code: {r.status_code}")
        return None
    mapfn = url.split('?')[0].split('/')[-1]
    if name:
        mapfn = f"{name.replace(' ','_')}-{mapfn}"

    if path is not None:
        path += '/' if path[-1] != '/' else ''
        outfn = path + mapfn
    else:
        outfn = mapfn
    with open('media/'+ outfn, 'wb') as f:
        f.write(r.content)
    return outfn

CAPS =  ' ABCDEFGHIJKLMNOPQRSTUVWXYZ'
SMALL = ' abcdefghijklmnopqrstuvwxyz'
def construct_id(name):
    c = name.split()[-1].upper()
    const = Constellation.objects.get(abbreviation=c)
    const_pk = f"{const.pk:02d}"
    parts = name.split()
    start = ''
    dindex = 0

    # Vnnn needs to be V0nnn
    if parts[0][0] == 'V':
        z = parts[0][1]
        rest = parts[0][1:]
        if rest[0].isdigit():
            return f"{const_pk}{int(rest):04d}"

    if len(parts) == 3:
        des = parts[0]
        component = str(parts[1]) # L 2 Pup
    else:
        des = parts[0] # greek or roman letter
        component = ''

    if des in BAYER_INDEX: # Greek letter
        start = '90'
        dindex = BAYER_INDEX.index(des)
    else:
        if len(des) == 1:
            if des in CAPS:
                start = '92'
                dindex = CAPS.index(des)
            elif des in SMALL:
                start = '91'
                dindex = SMALL.index(des)
    id = f"{const_pk}{start}{dindex:02d}{component}"
    return id

def process_star(name, maglimit=14.5, fov=60., debug=False):
    d = {}
    r = make_request(name, fov=fov, maglimit=maglimit)
    if not r:
        return d
    j = d['json'] = r.json()
    p = j['image_uri']
    fn = d['image_path'] = get_finder_chart(name, p)
    return d