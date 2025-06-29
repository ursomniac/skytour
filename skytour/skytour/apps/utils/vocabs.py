CATALOG_PRECEDENCE = [
    (1, '1 = Primary'),         # Messier, Caldwell
    (2, '2 = Important'),       # NGC, IC
    (3, '3 = Secondary'),       # Barnard, Collinder, Melotte, Sharpless
    (4, '4 = Collection'),      # Abell, Arp, Hickson, Stock, Trumpler, vdB
    (5, '5 = Ancillary'),       # Herschel 400
    (6, '6 = Survey'),          # LBN, LDN, PGC, UGC, PK
    (7, '7 = Other'),           # OTHER
    (8, '8 = Incidental'),      # Flamsteed, Bayer
    (9, '9 = Custom')           # Ast, Ast24
]

CATALOG_LOOKUP_CHOICES = (
    ('abbreviation', 'Abbreviation'),
    ('name', 'Catalog Name'),
    ('constellation', 'By Constellation'),
    ('other', 'Other Catalog'),
    ('custom', 'Custom')
)