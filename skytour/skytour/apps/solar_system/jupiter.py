import datetime, pytz
import math
from ..astro.time import get_julian_date, estimate_delta_t

sign = lambda a: 1 if a>0 else -1 if a<0 else 0

"""
GRS:

System II:  longitude = 9° (jan 2022), drifts 1.75°/month 
    best placed within 50m of transit time
"""
def get_jupiter_physical_ephem(utdt, planet, debug=False):
    dt = estimate_delta_t(utdt)
    jd = get_julian_date(utdt)
    jde = jd + dt/86400.
    d = jde - 2_451_545.0
    # Argument in the long-period term in the motion of Jupiter
    v = (172.74 + 1.115_88e-3 * d) % 360.
    # Mean anomalies of Earth and Jupiter
    m = (357.529 + 0.985_600_3 * d) % 360.
    n = (20.020 + 0.083_085_3 * d + 0.329 * math.sin(math.radians(v))) % 360.
    # Difference between the mean heliocentric longitudes of Earth and Jupiter
    j = (66.115 + 0.902_517_9 * d - 0.329 * math.sin(math.radians(v))) % 360.
    # Equations for the center of Earth and Jupiter
    a = (1.915 * math.sin(math.radians(m)) + 0.020 * math.sin(math.radians(m+m)))
    b = (5.555 * math.sin(math.radians(n)) + 0.168 * math.sin(math.radians(n+n)))

    if debug:
        print ("∆T: ", dt, "JD: ", jd, "JDE: ", jde)
        print ("d:", d, "V: ", v, "M: ", m, "N: ", n)
        print ("J: ", j, "A: ", a, "B: ", b)
    # then:
    k = j + a - b
    mul = sign(-1.*math.sin(math.radians(k)))
    # Radius Vector of the Earth
    rr = 1.00014 - 0.01671 * math.cos(math.radians(m)) - 1.4e-4*math.cos(math.radians(m+m))
    # Radius vector of Jupiter
    r = 5.20872 - 0.25208 * math.cos(math.radians(n)) - 6.11e-3*math.cos(math.radians(n+n))
    # Earth-Jupiter distance
    delta = math.sqrt(r*r + rr*rr - 2*r*rr*math.cos(math.radians(k)))
    # Phase angle Earth-Jupiter-Sun  (between ±12°)
    sin_psi = rr * math.sin(math.radians(k)) / delta
    psi = math.degrees(math.asin(sin_psi))

    if debug:
        print("K: ", k, 'R: ', rr, 'r: ', r, '∆: ', delta)
        print("sin Psi: ", sin_psi, "psi: ", psi)

    #
    x = d - delta/173.
    omega_1 = (210.98 + 877.816_908_8 * x + psi - b) % 360. # degrees
    omega_2 = (187.23 + 870.186_908_8 * x + psi - b) % 360. # degrees
    
    if debug: 
        print ("x: ", x, "omega1: ", omega_1, "omega2: ", omega_2)
    # phase correction
    psi2 = math.sin(math.radians(psi/2.))
    d_omega = mul * 57.3 * psi2**2.
    omega_1 += d_omega
    omega_2 += d_omega

    if debug: 
        print ("domega: ", d_omega, "omega1: ", omega_1, "omega2: ", omega_2)

    # Jupiter's Heliocentric longitude
    long = (34.35 + 0.083_091 * d + 0.329 * math.sin(math.radians(v)) + b) % 360.
    ds = 3.12 * math.sin(math.radians(long + 42.8)) # degrees
    de = ds - 2.22 * math.sin(math.radians(psi)) * math.cos(math.radians(long + 22)) \
        - (1.30 * (r - delta)/delta) * math.sin(math.radians(long - 100.5))
    
    if debug:
        print ("Long: ", long, "Ds: ", ds, "De: ", de)

    jupiter = dict(
        omega_1 = omega_1,
        omega_2 = omega_2,
        omega = omega_2,
        longitude = long,
        d_s = ds,
        d_e = de
    )
    jupiter['features'] = get_jupiter_features(utdt, jupiter, debug=False)
    return jupiter

def get_jupiter_features(utdt, jupiter, debug=False):
    """
    Assemble list of Jovian features (the GRS is the only one at present)
    and their current visiblity.
    """
    grs = get_red_spot(utdt, jupiter)
    features = [
        dict(
            name='Great Red Spot', 
            longitude=grs, 
            latitude=-22,
            system=0 # which rotational system to use
        )
    ]
    # index 0 is special for the GRS, 1, 2, 3 are for System I, II, III, respectively.
    rotation_speed = [ 877.27, 877.8169147, 870.1869147, 870.4535567 ] # degrees/day
    fdicts = []
    for feature in features:
        fdict = feature
        meridian = jupiter['omega_2'] if feature['system'] in [0,2] else jupiter['omega_1']
        ha_degrees = (meridian - feature['longitude']) # degrees from central meridian, positive is PAST it.
        if ha_degrees > 180.:
            ha_degrees -= 360.
        if ha_degrees < -180.:
            ha_degrees += 360.

        p_hours = 24.*360./rotation_speed[feature['system']]
        f = ha_degrees/360. # rotations
        dtt = p_hours * f
        if dtt < 0:  # still to come
            t_trans = utdt - datetime.timedelta(hours=dtt)
        else:
            t_trans = utdt - datetime.timedelta(hours=dtt) + datetime.timedelta(hours=p_hours)
        
        if debug:
            print ("Meridian: ", meridian, "Omega: ", jupiter['omega_2'])
            print ("HA: ", ha_degrees, "P hours: ", p_hours)
            print ("DTT: ", dtt, "T trans: ", t_trans)

        view = 'No'
        if abs(dtt) < 2.5:
            view = 'Edge'
        if abs(dtt) < 1:
            view = 'Possible'
        if abs(dtt) < 0.5:
            view = 'Best'

        fdict['meridian'] = meridian
        fdict['ha_deg'] = ha_degrees
        fdict['view'] = view
        fdict['next_transit'] = t_trans.isoformat()
        fdict['time_from_meridian'] = dtt
        fdicts.append(fdict)
    return fdicts

def get_red_spot(utdt, jupiter):
    """
    GRS:

    System II:  longitude = 9° (jan 2022), drifts 1.75°/month 
        best placed within 50m of transit time
    """
    u0 = datetime.datetime(2022, 1, 1, 0, 0).replace(tzinfo=pytz.utc)
    dd = utdt - u0
    delta_longitude = 1.75 * dd.days/30.6001
    # We could also do this with:
    # delta_longitude = 0.057189 * (jd - 2459580.5) # degrees
    grs = 9. + delta_longitude
    return grs

def get_all_system_longitude(utdt):
    """
    TEST: 
        From https://www.projectpluto.com/grs_form.htm
        This is just to test the mapping.

    TODO V2: stash this somewhere for future reference.
    """
    jd = get_julian_date(utdt)
    jup_mean = (jd - 2_455_636.938) * 360. / 4332.89709
    eqn_center = 5.55 * math.sin(jup_mean)
    angle = (jd - 2_451_870.628) * 360. / 398.884 - eqn_center
    correction = 11 * math.sin(angle) + 5 * math.cos(angle) - 1.25 * math.cos(jup_mean) - eqn_center
    cm1 = (156.84 + 877.8169147 * jd + correction) % 360.
    cm2 = (181.62 + 870.1869147 * jd + correction) % 360.
    cm3 = (138.41 + 870.4535567 * jd + correction) % 360.
    return dict(
        jd = jd, jup_mean = jup_mean, eqn_center = eqn_center, 
        correction = correction, sys_1 = cm1, sys_2 = cm2, sys_3 = cm3
    )