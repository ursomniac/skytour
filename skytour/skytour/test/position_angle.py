from cmath import atanh
import math

def plate_list():
    ldec = [90, 75, 60, 45, 30, 15, 0, -15, -30, -45, -60, -75, -90]
    lsize = [1, 12, 16, 20, 24, 32, 48, 32, 24, 20, 16, 12, 1]
    mul = [0., 2.0, 1.5, 1.2, 1.0, 0.75, 0.5, 0.75, 1.0, 1.2, 1.5, 2.0, 0.]
    plate = {}
    j = 1
    for i in range(len(ldec)):
        dec = ldec[i]
        if abs(dec) == 90:
            plate[j] = (0, dec)
            j += 1
            continue
        ras = [x * mul[i] for x in range(lsize[i])]
        for ra in ras:
            plate[j] = (ra, dec)
            j += 1
    return plate

def rad(ra, dec):
    rra = math.radians(ra*15.)
    rdec = math.radians(dec)
    return rra, rdec

def get_sep(ra1, dec1, ra2, dec2, degrees=True):
    dra = ra1 - ra2
    s1 = math.sin(dec1) * math.sin(dec2)
    s2 = math.cos(dec1) * math.cos(dec2) * math.cos(dra)
    sep = math.acos(s1 + s2)
    if degrees:
        sep = math.degrees(sep)
    return sep

def get_pa(ra1, dec1, ra2, dec2, degrees=True):
    dra = ra1 - ra2
    pa1 = math.sin(dra)
    pa2 = math.cos(dec2) * math.tan(dec1)
    pa3 = math.sin(dec2) * math.cos(dra)
    p = math.atan2(pa1, pa2-pa3)
    if degrees:
        p = math.degrees(p)
    return p #+ 180.#% 360.

def test_pa(center=None):
    center = (5., 30.) # ra dec
    xra, xdec = rad(center[0], center[1])

    for k, p in plate_list().items():
        zra, zdec = rad(p[0], p[1])
        sep = get_sep(xra, xdec, zra, zdec)
        pa = get_pa(xra, xdec, zra, zdec)
        if sep < 20. and sep > 0.:
            overlap = 10 - sep/2. 
            print (f"{k} = {p[0]}, {p[1]}: {sep:5.3f} at {pa:6.2f} by {overlap:5.2f}")

if __name__ == '__main__':
    test_pa()