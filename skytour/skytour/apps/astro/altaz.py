import math

### TODO V2: replace these with Skyfield calls, since I think they exist now.
# But I spent so much time typing these in!   :-)

COEFF_D = [ # 63 terms
     0, -2,  0,  0,  0,  0, -2,  0,  0, -2, -2, -2,  0,  2,  0,  2,  0,  0, -2,  0, 
     2,  0,  0, -2,  0, -2,  0,  0,  2, -2,  0, -2,  0,  0,  2,  2,  0, -2,  0,  2,
     2, -2, -2,  2,  2,  0, -2, -2,  0, -2, -2,  0, -1, -2,  1,  0,  0, -1,  0,  0,
     2,  0,  2
]
COEFF_M1 = [
     0,  0,  0,  0,  1,  0,  1,  0,  0, -1,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,
     0,  0,  0,  0,  0,  0,  0,  2,  0,  2,  1,  0, -1,  0,  0,  0,  1,  1, -1,  0,
     0,  0,  0,  0,  0, -1, -1,  0,  0,  0,  1,  0,  0,  1,  0,  0,  0, -1,  1, -1,
    -1,  0, -1
]
COEFF_M2 = [
     0,  0,  0,  0,  0,  1,  0,  0,  1,  0,  1,  0, -1,  0,  1, -1, -1,  1,  2, -2,
     0,  2,  2,  1,  0,  0, -1,  0, -1,  0,  0,  1,  0,  2, -1,  1,  0,  1,  0,  0,
     1,  2,  1, -2,  0,  1,  0,  0,  2,  2,  0,  1,  1,  0,  0,  1, -2,  1,  1,  1,
    -1,  3,  0
]
COEFF_F = [
     0,  2,  2,  0,  0,  0,  2,  2,  2,  2,  0,  2,  2,  0,  0,  2,  0,  2,  0,  2,
     2,  2,  0,  2,  2,  2,  2,  0,  0,  2,  0,  0,  0, -2,  2,  2,  2,  0,  2,  2,
     0,  2,  2,  0,  0,  0,  2,  0,  2,  0,  2, -2,  0,  0,  0,  2,  2,  0,  0,  2,
     2,  2,  2
]
COEFF_OMEGA = [
     1,  2,  2,  2,  0,  0,  2,  1,  2,  2,  0,  1,  2,  0,  1,  2,  1,  1,  0,  1,
     2,  2,  0,  2,  0,  0,  1,  0,  1,  2,  1,  1,  1,  0,  1,  2,  2,  0,  2,  1,
     0,  2,  1,  1,  1,  0,  1,  1,  1,  1,  1,  0,  0,  0,  0,  0,  2,  0,  0,  2,
     2,  2,  2
]
COEFF_DPSI = [
    -171996, -13187, -2274, 2062, 1426, 712, -517, -386, -301, 217, -158, 129, 123,
    63, 63, -59, -58, -51, 48, 46, -38, -31, 29, 29, 26, -22, 21, 17, 16, -16, -15,
    -13, -12, 11, -10, -8, 7, -7, -7, -7, 6, 6, 6, -6, -6, 5, -5, -5, -5, 4, 4, 4,
    -4, -4, -4, 3, -3, -3, -3, -3, -3, -3, -3
]
COEFF_DPSI_T = [
    -174.2, -1.6, -0.2, 0.2, -3.4, 0.1, 1.2, -0.4, 0, -0.5, 0, 0.1, 0, 0, 0.1, 0, -0.1, 
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, -0.1, 0, 0.1
] + [0]*33
COEFF_EPS = [
    92025, 5736, 977, -895, 54, -7, 224, 200, 129, -95, 0, -70, -53, 0, -33, 26, 32, 27,
    0, -24, 16, 13, 0, -12, 0, 0, -10, 0, -8, 7, 9, 7, 6, 0, 5, 3, -3, 0, 3, 3, 0, -3, 
    -3, 3, 3, 0, 3, 3, 3
] + [0]*14
COEFF_EPS_T = [
    8.9, -3.1, -0.5, 0.5, -0.1, 0, -0.6, 0, -0.1, 0.3
] + [0]*53

def get_nutation(t):
    """
    Full 63-term polynomial (Meeus, 1st Ed., p. 133)

    Returns: ∆psi and ∆eps, both in arcseconds.
    """
    d = math.radians((297.85036 + 445_267.11148 *t - 1.9142e-3 *t*t + t*t*t/189474.) % 360.)
    m1 = math.radians((357.52772 + 35999.05045 *t - 1.603e-4 *t*t - t*t*t/3.e5) % 360.)
    m2 = math.radians((134.96298 + 477_198.867398 *t + 8.6972e-3 *t*t + t*t*t/56_250.) % 360.)
    f = math.radians((93.27191 + 483_202.017538 *t - 3.6825e-3 *t*t + t*t*t/327_370.) % 360.)
    omega = math.radians((125.04452 - 1934.136261 *t + 2.0708e-3 *t*t + t*t*t/4.5e5) % 360.)

    # Assemble the 63 terms!
    arg_d = [d * x for x in COEFF_D]
    arg_m1 = [m1 * x for x in COEFF_M1]
    arg_m2 = [m2 * x for x in COEFF_M2]
    arg_f = [f * x for x in COEFF_F]
    arg_omega = [omega * x for x in COEFF_OMEGA]
    # Create the trig angles for the equation
    angles = []
    for args in zip(arg_d, arg_m1, arg_m2, arg_f, arg_omega):
        angles.append(sum(args))
    # Sum all the terms
    dpsi = 0.
    deps = 0.
    for i in range(63):
        dpsi += (COEFF_DPSI[i] + COEFF_DPSI_T[i] * t) * math.sin(angles[i]) # arcseconds * 1e4
        deps += (COEFF_EPS[i]  + COEFF_EPS_T[i] * t) * math.cos(angles[i])  # arcseconds * 1e4

    return dpsi/1.e4, deps/1.e4

def get_obliquity(t):
    """
    Good for Y = 2000 ± 10000 years.
    Returns: degrees
    """
    u = t/100.
    eps0 = 23. + 26/60 + 21.448/3600. # degrees
    deps0 = \
        - 4680.93 * u     \
        -    1.55 * u**2  \
        + 1999.25 * u**3  \
        -   51.38 * u**4  \
        -  249.67 * u**5  \
        -   39.05 * u**6  \
        +    7.12 * u**7  \
        +   27.87 * u**8  \
        +    5.79 * u**9  \
        +    2.45 * u**10
    eps = eps0 + deps0/3600.

    dpsi, deps = get_nutation(t)
    return eps + deps/3600.