DISTANCE_UNIT_CHOICES = [
    ('ly', 'Light Year'),
    ('kly', 'Kilo-Light Year'),
    ('Mly', 'Mega-Light Year'),
    ('pc', 'Parsec'),
    ('kpc', 'Kiloparsec'),
    ('Mpc', 'Megaparsec')
]

PRIORITY_CHOICES = [
    ('Highest', 'Highest'),
    ('High', 'High'),
    ('Medium', 'Medium'),
    ('Low', 'Low'),
    ('None', 'None')
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
    ['#0ff', '#FF0'], # not used
    ['#0cc', '#FC0'],
    ['#0aa', '#f90'],
    ['#088', '#f60'],
    ['#388', '#D40'],
    ['#688', '#C40']
]