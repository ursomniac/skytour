DISTANCE_UNIT_CHOICES = [
    ('ly', 'Light Year'),
    ('kly', 'Kilo-Light Year'),
    ('Mly', 'Mega-Light Year'),
    ('pc', 'Parsec'),
    ('kpc', 'Kiloparsec'),
    ('Mpc', 'Megaparsec')
]

PRIORITY_CHOICES = [
    ('Highest', '4 - Highest'),
    ('High', '3 - High'),
    ('Medium', '2 -Medium'),
    ('Low', '1 - Low'),
    ('None', '0 - None')
]

PRIORITY_COLORS = {
    'Highest': '#f00',
    'High': '#c90',
    'Medium': '#090',
    'Low': '#096',
    'None': '#ccc'
}
INT_YES_NO = (
    (0, 'No'),
    (1, 'Yes')
)

MILKY_WAY_CONTOUR_COLORS = [
    ['#0ff', '#FF0'], # this level is not used
    ['#0cc', '#FC0'], # level 1
    ['#0aa', '#f90'], # level 2
    ['#088', '#f60'], # level 3 - not used presently
    ['#388', '#D40'], # level 4 - not used presently
    ['#688', '#C40']  # level 5 - not used presently
]



"""
TODO: move all of the code reference to plot color choices to point to this dict.
"""
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