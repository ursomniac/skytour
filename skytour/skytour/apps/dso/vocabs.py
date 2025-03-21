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
    'Lowest': '#999',
    'None': '#999'
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