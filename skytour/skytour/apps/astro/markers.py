
def generate_equator(step=0.5, type='equ'):
    """
    step is in degrees
    types:
        equ = celestial equator
        ecl = ecliptic
        gal = galactic equator
    """
    d = 0.
    points = []
    while d <= 360.0:

        d += step
    pass

def generate_special_points():
    """
    This is a list of "special" points with their RA/DEC 2000 positions:
    """
    points = [
        dict(ra= 0.0000, dec= 90.0000, name='N. Celestial Pole', abbr='NCP'),
        dict(ra= 0.0000, dec=-90.0000, name='S. Celestial Pole', abbr='SCP'),
        dict(ra= 0.0000, dec=  0.0000, name='Vernal Equinox', abbr='VE'),
        dict(ra=12.0000, dec=  0.0000, name='Autumn Equinox', abbr='AE'),
        dict(ra=18.0000, dec= 66.5608, name='N. Ecl. Pole', abbr='NEP'),
        dict(ra= 6.0000, dec=-66.5608, name='S. Ecl. Pole', abbr='SEP'),
        dict(ra=12.8567, dec= 27.1167, name='N. Gal. Pole', abbr='NGP'),
        dict(ra= 0.8567, dec=-27.1167, name='S. Gal. Pole', abbr='SGP'),
        dict(ra=17.7600, dec=-28.9333, name='Galactic Center', abbr='GC'),
        dict(ra= 5.7600, dec= 28.9333, name='Galactic Anti-Center', abbr='GAC'),
    ]