DISTANCE_UNIT_CHOICES = [
    ('ly', 'Light Year'),
    ('kly', 'Kilo-Light Year'),
    ('Mly', 'Mega-Light Year'),
    ('pc', 'Parsec'),
    ('kpc', 'Kiloparsec'),
    ('Mpc', 'Megaparsec'),
    ('z', 'Redshift')
]

PRIORITY_CHOICES = [
    ('Highest', '4 - Highest'),
    ('High', '3 - High'),
    ('Medium', '2 -Medium'),
    ('Low', '1 - Low'),
    ('Lowest', '0 - None')
]

PRIORITY_VALUES = ['Lowest', 'Low', 'Medium', 'High', 'Highest']

PRIORITY_COLORS = {
    'Highest': '#f00',
    'High': '#c90',
    'Medium': '#090',
    'Low': '#096',
    'None': '#ccc'
}

MILKY_WAY_CONTOUR_COLORS = [
    ['#0ff', '#FF0'], # this level is not used
    ['#0cc', '#FC0'], # level 1
    ['#0aa', '#f90'], # level 2
    ['#088', '#f60'], # level 3 - not used presently
    ['#388', '#D40'], # level 4 - not used presently
    ['#688', '#C40']  # level 5 - not used presently
]

ATLAS_COLORS = {
    'milky-way-contours': [    
        ('#0ff', '#FF0'), # not used
        ('#0cc', '#FC0'), ('#0aa', '#f90'),
        ('#088', '#f60'), ('#388', '#D40'), ('#688', '#C40')
    ],
    'lines': {
        'equator': ('#f99', '#f9f'), 
        'ecliptic': ('#3c3', '#6ff'), 
        'galactic': ('#c6f', '#c6f')
    },
    'special-points': { 
        'symbol': ('#fa0', '#fa0'),
        'label': ('#666', '#ccc') 
    },
    'constellation': {
        'lines': ('#00f4', '#99f'),
        'boundaries': ('#999', '#9907'), 
        'markers':  { 'edge': ('#000', '#ffd'), 'label': ('#333', '#ffb'), 'background': ('#fff', '#333') },
    },
    'annotation':   ('#333', '#6ff'),
    'atlas-plate-reference': { 'label': ('#fff', '#777'), 'background': ('#ccc', '#444') },
}

SIMPLE_DSO_LIST = [
    19,   # C 22 (And)
    9,    # NGC 891 (And)
    52,   # M 31 (And)
    564,  # NGC 6781 (Aql)
    14,   # C 55 (Aqr)
    36,   # M 2 (Aqr)
    10,   # C 63 (Aqr)
    31,   # M 36 (Aur)
    30,   # M 37 (Aur)
    16,   # M 30 (Cap)
    1263, # C 92 (Car)
    1264, # C 102 (Car)
    47,   # M 52 (Cas)
    1337, # Ome Cen (Cen)
    100,  # M 41 (CMa)
    106,  # M 44 (Cnc)
    107,  # M 67 (Cnc)
    142,  # M 53 (Com)
    146,  # M 64 (Com)
    136,  # M 98 (Com)
    138,  # M 100 (Com)
    128,  # M 3 (CVn)
    130,  # M 63 (CVn)
    129,  # M 51 (CVn)
    131,  # M 94 (CVn)
    132,  # M 106 (CVn)
    251,  # C 20 (Cyg)
    254,  # NGC 6811 (Cyg)
    4,    # C 6 (Dra)
    194,  # M 102 (Dra)
    23,   # NGC 1232 (Eri)
    93,   # C 39 (Gem)
    32,   # M 35 (Gem)
    200,  # M 13 (Her)
    96,   # M 48 (Hya)
    120,  # C 59 (Hya)
    109,  # M 66 (Leo)
    111,  # M 96 (Leo)
    119,  # NGC 2903 (Leo)
    215,  # NGC 5897 (Lib)
    5,    # M 57 (Lyr)
    34,   # C 49 (Mon)
    #305,  # C 50 (Mon)
    35,   # NGC 2264
    191,  # M 10 (Oph)
    190,  # M 12 (Oph)
    192,  # M 107 (Oph)
    79,   # M 42 (Ori)
    87,   # NGC 2169
    262,  # M 15 (Peg)
    65,   # C 14 (Per)
    339,  # NGC 1245 (Per)
    603,  # NGC 1579 (Per)
    98,   # M 47 (Pup)
    645,  # NGC 2467
    58,   # C 65 (Scl)
    202,  # M 4 (Sco)
    204,  # M 6 (Sco)
    205,  # M 7 (Sco)
    243,  # M 11 (Sct)
    189,  # M 5 (Ser)
    230,  # M 16 (Ser)
    162,  # C 53 (Sex)
    223,  # M 8 (Sgr)
    229,  # M 17 (Sgr)
    236,  # M 20 (Sgr)
    224,  # M 22 (Sgr)
    227,  # M 24 (Sgr)
    231,  # M 55 (Sgr)
    1,    # M 1 (Tau)
    76,   # M 45 (Tau)
    20,   # M 33 (Tri)
    123,  # M 81 (UMa)
    #124,  # M 82 (UMa)
    127,  # M 97 (UMa)
    193,  # M 101 (UMa)
    279,  # M 61 (Vir)
    178,  # M 87 (Vir)
    283,  # M 104 (Vir)
    248,  # M 27 (Vul)
    247,  # Cr 399 (Vul)
]

OBSERVING_MODE_TYPES = [
    ('N', 'Naked Eye'),
    ('B', 'Binoculars'),
    ('S', 'Small Scope'),
    ('M', 'Medium Scope'),
    ('I', 'Imaging Scope')
]

STATUS_CHOICES = [
    (-9, 'Removed'),
    (0, 'Offline'),
    (1, 'Active')
]

MODE_VIABILITY_CHOICES = [
    (0, 'Not Viable'),          # typically set as a redetermination
    (1, 'Unlikely Viable'),     # experienced observers, great conditions, with luck
    (2, 'Extreme Difficulty'),  # experienced observers, great conditions
    (3, '(Very) Difficult'),    # experienced observers
    (4, 'Challenging'),         # generally requires great conditions
    (5, 'Requires Patience'),   # feasible but not particularly easy most of the time
    (6, 'Generally Visible'),   # feasible under decent conditions
    (7, 'Usually Easy'),        # feasible most of the time
    (8, 'Easy'),                # easy to find
    (9, 'Very Easy'),           # very easy to find
    (10, 'Extremely easy')      # even inexperienced observers have no problem
    # Typically the values will be 0, 2, 4/5, 8, 10
    # color scale:
    # 0 = black, 
    # 1-3: brown, red, orange
    # 4-6: yellow, chartreuse, green
    # 7-9: cyan, blue, purple
    # 10: white
]

VIABILITY_BACKGROUND_COLORS = [
    '#000', '#630', '#C00', '#F90', '#CC0', '#9C0', '#0A0', '#0CC', '#33C', '#90F', '#FFF'
]
VIABILITY_FOREGROUND_COLORS = [
    '#fff', '#fff', '#fff', '#000', '#000', '#000', '#000', '#000', '#fff', '#fff', '#000'
]

MODE_PRIORITY_CHOICES = [
    (0, 'Lowest'),
    (1, 'Low'),
    (2, 'Medium'),
    (3, 'High'),
    (4, 'Highest')
]

ISSUES_FLAGS = {
    # Not used in the model field, quick lookup
    'd': "Dim",
    's': "Small"
}