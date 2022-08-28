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
