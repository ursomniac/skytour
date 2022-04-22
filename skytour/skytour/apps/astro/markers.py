import math


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
            pass
        d += step
    return points


SPECIAL_POINTS = [
    dict(ra= 0.0000, dec= 90.0000, name='N. Celestial Pole', abbr='NCP'),
    dict(ra= 0.0000, dec=-90.0000, name='S. Celestial Pole', abbr='SCP'),
    dict(ra= 0.0000, dec=  0.0000, name='Vernal Equinox', abbr='VE'),
    dict(ra=12.0000, dec=  0.0000, name='Autumn Equinox', abbr='AE'),
    dict(ra=18.0000, dec= 66.5608, name='N. Ecl. Pole', abbr='NEP'),
    dict(ra= 6.0000, dec=-66.5608, name='S. Ecl. Pole', abbr='SEP'),     
    dict(ra=12.8567, dec= 27.1167, name='N. Gal. Pole', abbr='NGP'),         # b = 90
    dict(ra= 0.8567, dec=-27.1167, name='S. Gal. Pole', abbr='SGP'),         # b = -90
    dict(ra=17.7600, dec=-28.9333, name='Galactic Center', abbr='GC'),       # l, b = 0, 0
    dict(ra= 5.7600, dec= 28.9333, name='Galactic Anti-Center', abbr='GAC'), # l, b = 180, 0
]