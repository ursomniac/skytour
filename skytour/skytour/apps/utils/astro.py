import math

"""
def get_angular_distance(ra1, dec1, ra2, dec2):
    # This doesn't appear to be used anywhere, but keeping it around in case it gets useful.
    # Not useful for small angular distance
    dra = math.radians(15.*ra1 - 15.*ra2)
    d1 = math.sin(math.radians(dec1)) * math.sin(math.radians(dec2))
    d2 = math.cos(math.radians(dec1)) * math.cos(math.radians(dec2)) * math.cos(dra)
    return d1 + d2 # cosine
"""

def get_altitude(last, lat, ra, dec):
    ha = 15.*(last-ra)
    xha = math.radians(ha)
    s1 = math.sin(math.radians(lat)) * math.sin(math.radians(dec))
    s2 = math.cos(math.radians(lat)) * math.cos(math.radians(dec)) * math.cos(xha)
    return s1 + s2 # sine
