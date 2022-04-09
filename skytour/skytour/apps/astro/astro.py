import math

def get_altitude(last, lat, ra, dec):
    ha = 15.*(last-ra)
    xha = math.radians(ha)
    s1 = math.sin(math.radians(lat)) * math.sin(math.radians(dec))
    s2 = math.cos(math.radians(lat)) * math.cos(math.radians(dec)) * math.cos(xha)
    return s1 + s2 # sine
