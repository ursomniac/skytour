import math

def equ2ecl(ra, dec):
    e2000 = 23.4392911 # degrees
    rr = math.radians(ra * 15.)
    rd = math.radians(dec)
    re = math.radians(e2000)

    l1 = math.sin(rr) * math.cos(re)
    l2 = math.tan(rd) * math.sin(re)
    l3 = math.cos(ra)
    lam = math.atan2(l1 + l2, l3)
    
    b1 = math.sin(rd) * math.cos(re)
    b2 = math.cos(rd) * math.sin(re) * math.sin(rr)
    beta = math.asin(b1 - b2)

    return (math.degrees(lam) % 360., math.degrees(beta))

