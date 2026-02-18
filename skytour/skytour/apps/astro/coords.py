import math
import astropy.units as u
from astropy.coordinates import SkyCoord, Galactic

def old_equ2ecl(ra, dec):
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

def equ2ecl(ra, dec):
    #eq_coord = SkyCoord(ra=ra*15*u.degree, dec=dec*u.degree, frame='icrs')
    eq_coord = SkyCoord(ra=ra*15*u.degree, dec=dec*u.degree, frame='fk5', equinox='J2000')
    ecl_coord = eq_coord.transform_to('geocentricmeanecliptic')
    return(ecl_coord.lon.degree, ecl_coord.lat.degree)

def equ2gal(ra, dec):
    coord_icrs = SkyCoord(ra=ra*15. * u.degree, dec=dec * u.degree, frame='icrs')
    coord_galactic = coord_icrs.transform_to(Galactic())
    return (coord_galactic.l.degree, coord_galactic.b.degree)