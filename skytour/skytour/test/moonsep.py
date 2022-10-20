from ..apps.astro.angdist import get_small_ang_sep

SK = {
    'neptune':  { 'ra': 23.59539061,   'dec': -3.954859308,
    'moons': {
        'triton':   { 'ra': 23.59504591,   'dec': -3.953406977  },
    }},
    'jupiter':  { 'ra':  0.0719190323, 'dec': -1.2682514989, 
    'moons': {
        'io':       { 'ra':  0.0733479628, 'dec': -1.2564766132 },
        'europa':   { 'ra':  0.0698793103, 'dec': -1.2856785138 },
        'ganymede': { 'ra':  0.0698107938, 'dec': -1.2876189223 },
        'callisto': { 'ra':  0.0817501286, 'dec': -1.1959812056 },
    }}
}  
ST = {
    'neptune':  { 'ra': 23.595416667,  'dec': -3.954750000  ,
    'moons': {
        'triton':   { 'ra': 23.595333333,  'dec': -3.952166667  },
    }},
    'jupiter':  { 'ra':  0.0719444444, 'dec': -1.2686111111 ,
    'moons': {
        'io':       { 'ra':  0.0736861111, 'dec': -1.2548888889 },
        'europa':   { 'ra':  0.0702166667, 'dec': -1.2840833333 },
        'ganymede': { 'ra':  0.0696527778, 'dec': -1.2891666667 },
        'callisto': { 'ra':  0.0820888889, 'dec': -1.1943611111 },
    }},
}


def to_float(t):
    d = abs(t[0])
    d += t[1]/60.
    d += t[2]/3600.
    d *= 1. if t[0] >= 0 else -1.
    return d

def test1(planet):
    sk_pra =  SK[planet]['ra']
    sk_pdec = SK[planet]['dec']
    st_pra =  ST[planet]['ra']
    st_pdec = ST[planet]['dec']

    for moon in SK[planet]['moons'].keys():
        sk_m_ra =  SK[planet]['moons'][moon]['ra']
        sk_m_dec = SK[planet]['moons'][moon]['dec']
        sk_dist = get_small_ang_sep(sk_pra, sk_pdec, sk_m_ra, sk_m_dec) * 3600.

        st_m_ra =  ST[planet]['moons'][moon]['ra']
        st_m_dec = ST[planet]['moons'][moon]['dec']
        st_dist = get_small_ang_sep(st_pra, st_pdec, st_m_ra, st_m_dec) * 3600.

        print(f"Skytour:    {planet} to {moon} = {sk_dist:8.4f}\"")
        print(f"Stellarium: {planet} to {moon} = {st_dist:8.4f}\"")
