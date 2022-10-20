import math

def get_altitude(last, lat, ra, dec):
    """
    At a given local apparent sidereal time, and latitude,
    get the altitude of an object at coordinates (ra, dec).
    """
    ha = 15.*(last-ra)
    xha = math.radians(ha)
    s1 = math.sin(math.radians(lat)) * math.sin(math.radians(dec))
    s2 = math.cos(math.radians(lat)) * math.cos(math.radians(dec)) * math.cos(xha)
    return s1 + s2 # sine of the altitude

def solar_system_apparent_magnitude(
        earth_dist,
        sun_dist,
        h,
        phase_angle,
        g = 0.15
    ):
    """
    Stellarium uses:

    d = 5.* math.log(dr)
    phase in DEGREES

    Io: -1.68 + d + phaseDeg * (0.046 - 0.0010*phaseDeg)
    Europa: -1.41 + d + phaseDeg * (0.0312 - 0.00125*phaseDeg)
    Ganymede: -2.09 + d + phaseDeg * (0.0323 - 0.00066*phaseDeg)
    Callisto: -1.05 + d + phaseDeg * (0.078 - 0.00274*phaseDeg)
    """
    m1 = h + 5 * math.log10(sun_dist * earth_dist)
    if phase_angle:
        rpa = math.radians(phase_angle) # Assuming this is the same phase angle
        phi_1 = math.exp(-3.33 * math.tan(rpa/2.)**0.63)
        phi_2 = math.exp(-1.87 * math.tan(rpa/2.)**1.22)
        m2 = 2.5 * math.log10((1 - g) * phi_1 + g * phi_2)
    else:
        m2 = -g
    mag = m1 - m2
    return mag

def galilean_magnitude(name, h, phi, d_e, d_s):
    terms = {
        'Io':        [0.046,  0.0010],
        'Europa':    [0.0312, 0.00125],
        'Ganymede':  [0.0323, 0.00066],
        'Callisto':  [0.078,  0.00274]
    }
    d = 5. * math.log10(d_e * d_s)
    mag = h + d + phi*(terms[name][0] - terms[name][1]*phi)
    return mag

