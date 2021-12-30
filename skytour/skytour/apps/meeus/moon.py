import math
from .nutation import get_nutation
from .coord import ecl2equ

# Longitude and Distance coefficients - 60 terms
COEFF_SL = [
    6_288_774, 1_274_027, 658_314, 213_618, -185_116, -114_332, 58_793, 57_066, 53_322, 45_758, 
    -40_923, -34_720, -30_383, 15_327, -12_528, 10_980, 10_675, 10_034, 8_548, -7_888,
    -6_766, -5_163, 4_987, 4_036, 3_994,    3_861, 3_665, -2_689, -2_602, 2_390,
    -2_348, 2_236, -2_120, -2_069, 2_048,   -1_773, -1_595, 1_215, -1_110, -892,
    -810, 759, -713, -700, 691,      596, 549, 537, 520, -487,
    -399, -381, 351, -340, 330,      327, -323, 299, 294, 0
]
COEFF_SR = [
    -20_905_355, -3_699_111, -2_955_968, -569_925, 48_888, 
    -3_149, 246_158, -152_138, -170_733, -204_586, 
    -129_620, 108_743, 104_755, 10_321, 0, 79_661, -34_782, -23_210, -21_636, 24_208,
    30_824, -8_379, -16_675, -12_831, -10_445, -11_650, 14_403, -7_003, 0, 10_056,
    6_322, -9_884, 5_751, 0, -4_950,   4_130, 0, -3_958, 0, 3_258,
    2_616, -1_897, -2_117, 2_354, 0,   0, -1_423, -1_117, -1_571, -1_739,
    0, -4_421, 0, 0, 0,   0, 1_165, 0, 0, 8_752  
]
COEFF_LR_D =  [ 
     0,  2,  2,  0,  0,  0,  2,  2,  2,  2,     0,  1,  0,  2,  0,  0,  4,  0,  4,  2,
     2,  1,  1,  2,  2,  4,  2,  0,  2,  2,     1,  2,  0,  0,  2,  2,  2,  4,  0,  3,
     2,  4,  0,  2,  2,  2,  4,  0,  4,  1,     2,  0,  1,  3,  4,  2,  0,  1,  2,  2
]
COEFF_LR_M =  [
     0,  0,  0,  0,  1,  0,  0, -1,  0, -1,     1,  0,  1,  0,  0,  0,  0,  0,  0,  1,
     1,  0,  1, -1,  0,  0,  0,  1,  0, -1,     0, -2,  1,  2, -2,  0,  0, -1,  0,  0,
     1, -1,  2,  2,  1, -1,  0,  0, -1,  0,     1,  0,  1,  0,  0, -1,  2,  1,  0,  0
]
COEFF_LR_MP = [
     1, -1,  0,  2,  0,  0, -2, -1,  1,  0,    -1,  0,  1,  0,  1,  1, -1,  3, -2, -1,
     0, -1,  0,  1,  2,  0, -3, -2, -1, -2,     1,  0,  2,  0, -1,  1,  0, -1,  2, -1,
     1, -2, -1, -1, -2,  0,  1,  4,  0, -2,     0,  2,  1, -2, -3,  2,  1, -1,  3, -1
]
COEFF_LR_F =  [
     0,  0,  0,  0,  0,  2,  0,  0,  0,  0,     0,  0,  0, -2,  2, -2,  0,  0,  0,  0,
     0,  0,  0,  0,  0,  0,  0,  0,  2,  0,     0,  0,  0,  0,  0, -2,  2,  0,  2,  0,
     0,  0,  0,  0,  0, -2,  0,  0,  0,  0,    -2, -2,  0,  0,  0,  0,  0,  0,  0, -2
]
# Latitude coefficients - 60 terms
COEFF_B = [
    5_128_122, 280_602, 277_693, 173_237, 55_413,  46_271, 32_573, 17_198, 9_266, 8_822,
    8_216, 4_324, 4_200, -3_359, 2_463,        2_211, 2_065, -1_870, 1_828, -1_794,
    -1_749, -1_565, -1_491, -1_475, -1_410,    -1_344, -1_335, 1_107, 1_021, 833,
    777, 671, 607, 596, 491,  -451, 439, 422, 421, -366, -351, 331, 315, 302, -283,
    -229, 223, 223, -220, -220, -185, 181, -177, 176, 166, -164, 132, -119, 115, 107
]
COEFF_B_D = [
     0,  0,  0,  2,  2,  2,  2,  0,  2,  0,     2,  2,  2,  2,  2,  2,  2,  0,  4,  0,
     0,  0,  1,  0,  0,  0,  1,  0,  4,  4,     0,  4,  2,  2,  2,  2,  0,  2,  2,  2,
     2,  4,  2,  2,  0,  2,  1,  1,  0,  2,     1,  2,  0,  4,  4,  1,  4,  1,  4,  2  
]
COEFF_B_M = [
     0,  0,  0,  0,  0,  0,  0,  0,  0,  0,    -1,  0,  0,  1, -1, -1, -1,  1,  0,  1,
     0,  1,  0,  1,  1,  1,  0,  0,  0,  0,     0,  0,  0,  0, -1,  0,  0,  0,  0,  1,
     1,  0, -1, -2,  0,  1,  1,  1,  1,  1,     0, -1,  1,  0, -1,  0,  0,  0,  1, -2
]
COEFF_B_MP = [
     0,  1,  1,  0, -1, -1,  0,  2,  1,  2,     0, -2,  1,  0, -1,  0, -1, -1, -1,  0,
     0, -1,  0,  1,  1,  0,  0,  3,  0, -1,     1, -2,  0,  2,  1, -2,  3,  2, -3, -1, 
     0,  0,  1,  0,  1,  1,  0,  0, -2, -1,     1, -2,  2, -2, -1,  1,  1, -1,  0,  0
]
COEFF_B_F = [
     1,  1, -1, -1,  1, -1,  1,  1, -1, -1,    -1, -1,  1, -1,  1,  1, -1, -1, -1,  1,
     3,  1,  1,  1, -1, -1, -1,  1, -1,  1,    -3,  1, -3, -1, -1,  1, -1,  1, -1,  1,
     1,  1,  1, -1,  3, -1, -1,  1, -1, -1,     1, -1,  1, -1, -1, -1, -1, -1, -1,  1 
]

def moon_lon_lat(t, dpsi=None, debug=False, return_dict=False):
    """
    Meeus, 1st Ed. Chapter 45
    """
    # Moon's mean longitude
    lp = math.radians((
        218.316_4391 
        + 481_267.881_342_36 * t 
        - 1.3268e-3 * t**2 
        + t**3/538_841. 
        - t**4/65_194_000.
    ) % 360.)
    # Mean elongation of the Moon
    d = math.radians((
        297.850_2042 
        + 445_267.111_5168 * t 
        - 1.63e-3 * t**2 
        + t**3/545_868. 
        - t**4/113_065_000.
    ) % 360.) 
    # Sun's Mean Anomaly
    m = math.radians((
        357.529_1092 
        + 35_999.050_2909 * t 
        - 1.536e-4 * t**2 
        + t**3/24_490_000.
    ) % 360.)
    # Moon's Mean Anomaly
    mp = math.radians((
        134.963_4114
        + 477_198.867_6313 * t
        + 8.997e-3 * t**2
        + t**3 / 69_699.
        - t**4 / 14_712_000.
    ) % 360.)
    # Moon's Argument of Latitude
    f = math.radians((
        93.272_0993
        + 483_202.017_5273 * t
        - 3.4029e-3 * t**2
        - t**3 / 3_526_000.
        + t**4 / 863_31.
    ) % 360.)

    # planetary influences
    a1 = math.radians((119.75 + 131.849 * t) % 360.)     # Venus
    a2 = math.radians(( 53.09 + 479_264.29 * t) % 360.)  # Jupiter
    a3 = math.radians((313.45 + 481_266.484 * t) % 360.) # Flattening of the Earth

    # Account for the decreasing eccentricity of the Earth's orbit:
    # These get applied to all M terms
    e = 1 - 0.002516 * t - 7.4e-6 * t**2

    # Correct the M terms with this:
    el_fudge = []
    eb_fudge = []
    for i in range(60):
        zl = abs(COEFF_LR_M[i])
        if zl == 1:
            el_fudge.append(e)
        elif zl == 2:
            el_fudge.append(e**2)
        else:
            el_fudge.append(1.)
        zb = abs(COEFF_B_M[i])
        if zb == 1:
            eb_fudge.append(e)
        elif zb == 2:
            eb_fudge.append(e**2)
        else:
            eb_fudge.append(1.)

    if debug:
        print ("L\': ", math.degrees(lp))
        print ("D: ", math.degrees(d))
        print ("M: ", math.degrees(m))
        print ("MP: ", math.degrees(mp))
        print ("F: ", math.degrees(f))
        print ("A1: ", math.degrees(a1))
        print ("A2: ", math.degrees(a2))
        print ("A3: ", math.degrees(a3))
        print ("E: ", e)

    ### Longitude and Distance
    # Combine terms for the equation
    larg_d  = [d  * x for x in COEFF_LR_D]
    larg_m  = [m  * x for x in COEFF_LR_M]
    larg_mp = [mp * x for x in COEFF_LR_MP]
    larg_f  = [f  * x for x in COEFF_LR_F]
    
    # Now do the sums
    l_angles = []
    for args in zip(larg_d, larg_m, larg_mp, larg_f):
        l_angles.append(sum(args))

    sigma_l = 0.
    sigma_r = 0.
    for i in range(60):
        sigma_l += COEFF_SL[i] * math.sin(l_angles[i]) * el_fudge[i] # micro-degrees
        sigma_r += COEFF_SR[i] * math.cos(l_angles[i]) # meters

    ### Latitude
    # Combine terms for the equation
    barg_d  = [d  * x for x in COEFF_B_D]
    barg_m  = [m  * x for x in COEFF_B_M]
    barg_mp = [mp * x for x in COEFF_B_MP]
    barg_f  = [f  * x for x in COEFF_B_F]
    # Do the Sums
    b_angles = []
    for args in zip(barg_d, barg_m, barg_mp, barg_f):
        b_angles.append(sum(args))

    sigma_b = 0.
    for i in range(60):
        sigma_b += COEFF_B[i] * math.sin(b_angles[i]) * eb_fudge[i] # micro-degrees

    # Apply corrections
    sigma_l += (3958 * math.sin(a1) + 1962 * math.sin(lp - f) + 318 * math.sin(a2))
    sigma_b += (-2235 * math.sin(lp) + 382 * math.sin(a3) + 175 * math.sin(a1 - f)
        + 175 * math.sin(a1 + f) + 127 * math.sin(lp - mp) - 115 * math.sin(lp + mp)
    )

    if debug:
        print ("∑l: ", sigma_l)
        print ("∑b: ", sigma_b)
        print ("∑r: ", sigma_r)

 
    if not dpsi:
        (dpsi, deps) = get_nutation(t)
    moon_longitude = math.degrees(lp) + sigma_l/1.e6 + dpsi/3600.
    moon_latitude = sigma_b/1.e6
    moon_distance = 385000.56 + sigma_r/1000.
    angular_size = math.asin(6378.14 / moon_distance) * 3600. # degrees


    if debug:
        print ("Longitude: ", moon_longitude)
        print ("Latitude: ", moon_latitude)
        print ("Distance: ", moon_distance)
        print ("Ang. Diameter: ", angular_size)

    if return_dict:
        return {
            'latitude': moon_latitude, 
            'longitude': moon_longitude, 
            'distance': moon_distance, 
            'angular_diameter': angular_size 
        }
    return(moon_latitude, moon_longitude, moon_distance, angular_size)

MOON_PHASES = ['NEW MOON', 'WAXING CRESCENT', 'FIRST QUARTER', 'WAXING GIBBOUS', 'FULL MOON', 
    'WANING GIBBOUS', 'LAST QUARTER', 'WANING CRESCENT', 'NEW MOON'
]

def simple_lunar_phase(jd, return_dict=False):
    lunar_period = 29.530588853
    lunations = (jd - 2451550.1) / lunar_period
    percent = lunations - int(lunations)
    phase_angle = percent * 360.
    delta_t = phase_angle * lunar_period / 360.
    moon_day = int(delta_t + 0.5)
    phase = MOON_PHASES[int((phase_angle + 22.5) / 45.)]
    if return_dict:
        return {
            'angle': phase_angle, 
            'day': moon_day, 
            'phase': phase, 
            'days_since_new_moon': delta_t
        }
    return phase_angle, phase, moon_day, delta_t