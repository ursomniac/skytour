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
