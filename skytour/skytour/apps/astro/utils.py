import math

def get_limiting_magnitude(bortle):
    """
    Return the expected limiting magnitude (zenith) for a Bortle value.
    """
    if bortle is None:
        return None
    vrange = [
        None, '≥ 7.5', '7.0 - 7.5', '6.5 - 7.0',
        '6.0 - 6.5', '5.5 - 6.0', '5.0 - 5.5',
        '4.5 - 5.0', '4.0 - 4.5', '< 4.0'
    ]
    return vrange[bortle]

def get_apparent_magnitude(h, r_sun_target, r_earth_target, beta, g=0.15):
    """
    H: absolute magnitude (solar system)
    r: distance from body to Sun
    delta: distance from body to Earth
    beta: phase angle (degrees)
    g: slope parameter: defaults to 0.15 
    """
    rpa = math.radians(beta) # Assuming this is the same phase angle
    phi_1 = math.exp(-3.33 * math.tan(rpa/2.)**0.63)
    phi_2 = math.exp(-1.87 * math.tan(rpa/2.)**1.22)
    m1 = h + 5 * math.log10(r_sun_target * r_earth_target) 
    m2 = 2.5 * math.log10((1 - g) * phi_1 + g * phi_2)
    mag = m1 - m2
    return mag

def get_sep(ra1, dec1, ra2, dec2):
    """
    Return angular separation (degrees) between two coordinates.
    This will NOT WORK for small angular separations (cos d ---> 1 - tiny number).
    """
    dra = ra1 - ra2
    dt1 = math.sin(dec1) * math.sin(dec2)
    dt2 = math.cos(dec1) * math.cos(dec2) * math.cos(dra)
    cos_d = dt1 + dt2
    sep = math.degrees(math.acos(cos_d))
    return sep

def get_small_sep(ra1, dec1, ra2, dec2):
    """
    for small separations
    """
    dra = (ra2 - ra1) * 15.
    ddec = (dec2 - dec1)
    x = dra * math.cos(math.radians(ddec))
    y = x*x + ddec*ddec
    return math.sqrt(y)

def alt_get_small_sep(ra1, dec1, ra2, dec2, unit='deg', debug=False):

    r1 = math.radians(ra1*15)
    r2 = math.radians(ra2*15)
    d1 = math.radians(dec1)
    d2 = math.radians(dec2)

    cd1 = math.cos(d1)
    cd2 = math.cos(d2)
    cdr = math.cos(r2 - r1)
    sdr = math.sin(r2 - r1)
    sd1 = math.sin(d1)
    sd2 = math.sin(d2)

    x = (cd1 * sd2) - (sd1 * cd2 * cdr)
    y = cd2 * sdr
    z = (sd1 * sd2) + (cd1 * cd2 * cdr)

    xy = math.sqrt((x * x) + (y * y))
    tand = xy/z
    dd = math.atan2(xy, z)
    dd0 = math.degrees(dd)

    if debug:
        print(f"X: {x:.4f}  Y: {y:.4f}  Z: {z:.4f}")
        print(f"tan d: {tand:.4f}")
        print(f" = {xy:.4f} / {z:.4f} ")
        print(f"d: {dd:.4f} rad = {math.degrees(dd):.4f} deg")

    if unit in ['deg', 'd', '°']:
        return dd0
    elif unit in ['arcmin', 'm', '\'']:
        return dd0 * 60.
    elif unit in ['arcsec', 's', '\"']:
        return dd0 * 3600.
    else: # return radians
        return dd

def get_simple_position_angle(ra1, dec1, ra2, dec2):
    # Positive east
    xra1 = math.radians(ra1 * 15.)
    xra2 = math.radians(ra2 * 15.)
    dra = xra1 - xra2
    xdec1 = math.radians(dec1)
    xdec2 = math.radians(dec2)

    pa1 = math.sin(dra)
    pa2 = math.cos(xdec2) * math.tan(xdec1) 
    pa3 = math.sin(xdec2) * math.cos(dra)
    pa = (math.degrees(math.atan2(pa1, pa2-pa3)) + 180.)
    pa %= 360.
    return pa

def get_size_from_logd25(x, ratio=0., raw=False):
    """
    LEDA, etc. stores angular size as log d25 in 0.1 arcmins.
    """
    major = 10. ** (x - 1.)
    minor = major / (10. ** ratio)
    if raw:
        return (major, minor)
    else:
        return f"{major:.3f}\' x {minor:.3f}\'"

def get_distance_from_modulus(mu, units='mly'):
    mult = {'pc': 1, 'kpc': 1.e-3, 'mpc': 1.e-6, 'ly': 3.26, 'kly': 3.26e-3, 'mly': 3.26e-6}
    x = 1. + mu / 5.
    d = 10. ** x # parsecs
    if units in mult.keys():
        d *= mult[units]
    return d

def sqs_to_sqm(sqs):
    return sqs - 8.89

def sqm_to_sqs(sqm):
    return sqm + 8.89