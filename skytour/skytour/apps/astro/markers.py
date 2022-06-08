import math
from re import X
from xml.dom import xmlbuilder


def generate_equator(step=0.5, type='equ'):
    """
    step is in degrees
    types:
        equ = celestial equator
        ecl = ecliptic
        gal = galactic equator
    """
    eps = math.radians(23.4392911)
    se = math.sin(eps)
    ce = math.cos(eps)
    d = 0.
    points = []
    while d <= 360.0:
        rx = math.radians(d)
        sx = math.sin(rx)
        cx = math.cos(rx)
        if type == 'equ':
            points.append(tuple([d, 0.]))
        elif type == 'ecl':
            # Because beta is 0, some terms cancel out
            ra = math.degrees(math.atan2(sx * ce,  cx)) / 15.
            dec = math.degrees(math.asin(se * sx)) 
            points.append(tuple([ra, dec]))
        elif type == 'gal':
            ra, dec = gal2equ(d, 0)
            points.append(tuple([ra, dec]))
        d += step
    return points


SPECIAL_POINTS = [
    dict(ra= 0.0000, dec= 90.0000, name='N. Celestial Pole', abbr='NCP'),
    dict(ra= 0.0000, dec=-90.0000, name='S. Celestial Pole', abbr='SCP'),
    dict(ra= 0.0000, dec=  0.0000, name='Vernal Equinox', abbr='VEq'),
    dict(ra=12.0000, dec=  0.0000, name='Autumn Equinox', abbr='AEq'),
    dict(ra=18.0000, dec= 66.5608, name='N. Ecl. Pole', abbr='NEP'),
    dict(ra= 6.0000, dec=-66.5608, name='S. Ecl. Pole', abbr='SEP'),     
    dict(ra=12.8567, dec= 27.1167, name='N. Gal. Pole', abbr='NGP'),         # b = 90
    dict(ra= 0.8567, dec=-27.1167, name='S. Gal. Pole', abbr='SGP'),         # b = -90
    dict(ra=17.7600, dec=-28.9333, name='Galactic Center', abbr='GalCen'),       # l, b = 0, 0
    dict(ra= 5.7600, dec= 28.9333, name='Galactic Anti-Center', abbr='GAC'), # l, b = 180, 0
]

def b1950toj2000(ra, dec):
    """
    Quick conversion from B1950 coordinates to J2000.
    This is used for generating the galactic equator, whose definition is based on B1950 coordinates.
    """
    xra = math.radians(ra)
    xdec = math.radians(dec)
    jra = ra + 0.640265 + 0.278369 * math.sin(xra) * math.tan(xdec)
    jdec = dec + 0.278369 * math.cos(xra)
    return jra, jdec

def gal2equ(l, b, epoch=2000):
    """
    Convert galactic (l, b) coordinates to ra, dec (B1950 epoch).
    If epoch == 2000, then convert the B1950 ra, dec coordinates to J2000.
    """
    xl = math.radians(l - 123.)
    xb = math.radians(b)
    xe = math.radians(27.4)

    sxl = math.sin(xl)
    cxl = math.cos(xl)
    sxe = math.sin(xe)
    cxe = math.cos(xe)
    sxb = math.sin(xb)
    cxb = math.cos(xb)

    xd = cxl * sxe - math.tan(xb) * cxe
    x = math.atan2(sxl, xd)
    ra = (math.degrees(x) + 12.25) % 360.

    xdec = math.asin(sxb * sxe + cxb * cxe * cxl)
    dec = math.degrees(xdec)

    if epoch != 1950: # since b is always zero, this is OK
        jra, jdec = b1950toj2000(ra, dec)
        return jra / 15., jdec

    return ra / 15., dec




