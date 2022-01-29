# Is this needed?  If so, shouldn't it be a setting?
HOME_LONGITUDE = 73. +  6./60. + 58./3600.
HOME_LATITUDE  = 42. + 37./60. + 14./3600.

MAP_SYMBOL_TYPES = [
    ('marker', 'Marker'),                               # default - star like things, or unknown
    ('ellipse', 'Ellipse'),                             # galaxies - maybe not irregular
    ('open-circle', 'Open Circle'),                     # open clusters, associations
    ('gray-circle', 'Gray Circle'),                     # 
    ('circle-square', 'Circle in Square'),              # planetary nebulae
    ('square', 'Open Square'),                          # Emission Nebulae
    ('gray-square', 'Gray Square'),                     # Dark Nebulae
    ('circle-gray-square', 'Circle in Gray Square'),    # cluster w/ nebulosity
    ('circle-plus', 'Circle Plus')                      # globular clusters
]