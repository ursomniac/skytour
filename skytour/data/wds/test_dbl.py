
"""
    COLUMN     Format                     DATA
    --------   ------         ----------------------------
    1  -  10   A10             2000 Coordinates
    11 -  17   A7              Discoverer & Number
    18 -  22   A5              Components
    24 -  27   I4              Date (first)
    29 -  32   I4              Date (last)
    34 -  37   I4              Number of Observations (up to 9999)
    39 -  41   I3              Position Angle (first - XXX)
    43 -  45   I3              Position Angle (last  - XXX)
    47 -  51   F5.1            Separation (first)
    53 -  57   F5.1            Separation (last)
    59 -  63   F5.2            Magnitude of First Component
    65 -  69   F5.2            Magnitude of Second Component
    71 -  79   A9              Spectral Type (Primary/Secondary)
    81 -  84   I4              Primary Proper Motion (RA)
    85 -  88   I4              Primary Proper Motion (Dec)
    90 -  93   I4              Secondary Proper Motion (RA)
    94 -  97   I4              Secondary Proper Motion (Dec)
    99 - 106   A8              Durchmusterung Number
   108 - 111   A4              Notes
   113 - 130   A18             2000 arcsecond coordinates
"""

def extract_field(s, start, end, format):
    f = s[start-1:end]
    try:
        if format[0] == 'A':
            return f.strip()
        elif format[0] == 'I':
            return int(f)
        elif format[0] == 'F':
            return float(f)
        else:
            return f
    except:
        return None
    
def check_notes(flag, notes):
    return flag in notes

def get_sep(s):
    return float(s[52:57])

def get_notes(s):
    return s[107:111]

def get_coords(s):
    return s[:10]

def find_dupe_coords(lines):
    found = []
    dupes = {}
    for line in lines:
        c = get_coords(line)
        if c in found:
            if c not in dupes.keys():
                dupes[c] = 2
            else:
                dupes[c] += 1
        else:
            found.append(c)
    return dupes



FIELD_LIST = [
   (  1,  10,  'A10',  'coord', '2000 Coordinates'),
   ( 11,  17,   'A7',   'name', 'Discoverer & Number'),
   ( 18,  22,   'A5',  'comps', 'Components'), 
   ( 24,  27,   'I4',  'year0', 'Date - first'),
   ( 29,  32,   'I4',  'year1', 'Date - last'),
   ( 34,  37,   'I4',  'n_obs', 'Number of Observations'),
   ( 39,  41,   'I3', 'theta0', 'Position Angle - first'),
   ( 43,  45,   'I3', 'theta1', 'Position Angle - last'),
   ( 47,  51, 'F5.1',   'rho0', 'Separation - first'),
   ( 53,  57, 'F5.1',   'rho1', 'Separation - last'),
   ( 59,  63, 'F5.2',   'mag0', 'Magnitude of First Component'),
   ( 65,  69, 'F5.2',   'mag1', 'Magnitude of Second Component'),
   ( 71,  79,   'A9',  'spect', 'Spectral Type (Primary/Secondary'),
   ( 81,  84,   'I4',  'pmra0', 'Primary Proper Motion - RA'),
   ( 85,  88,   'I4', 'pmdec0', 'Primary Proper Motion - Dec'),
   ( 90,  93,   'I4',  'pmra1', 'Secondary Proper Motion - RA'),
   ( 94,  97,   'I4', 'pmdec1', 'Secondary Proper Motion - Dec'),
   ( 99, 106,   'A8',  'bd_id', 'Durchmusterung Number'),
   (108, 111,   'A4',  'notes', 'Notes'),
   (113, 130,  'A18', 'jcoord', '2000 arcsecond coordinates'),
   (133, 136,   'A3',  'const', 'Constellation'),
   (138, 150,  'A13', 'proper', 'Proper Name')
]

def get_data():
    data = []
    with open('data/wds/wds.summ_con.txt') as f:
        lines = [x.strip() for x in f.readlines()]
        f.close()
    for line in lines:
        if len(line) < 113:
            continue
        data.append(line)
    return data