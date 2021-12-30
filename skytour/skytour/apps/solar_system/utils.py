import math
from skyfield.api import load
from ..meeus.almanac import get_julian_date, get_t_epoch
from ..meeus.coord import get_alt_az
from .saturn import saturn_ring
from .vocabs import EPHEMERIS, DIAMETERS

def get_angular_size(diameter, distance, units='arcsec'):  # text name, e.g., 'Mars'
    #print ("DIAMETER: ", diameter, 'DISTANCE: ', distance)
    theta = math.degrees(math.asin(diameter/distance)) * 3600. # arcsec
    if units == 'arcmin':
        return theta / 60.
    if units == 'degrees':
        return theta / 3600.
    return theta

MAG = {
    'Mercury': -0.42, 'Venus': -4.40, 'Mars': -1.52, 'Jupiter': -9.40,
    'Saturn': -8.88, 'Uranus': -7.19, 'Neptune': -6.87, 'Pluto': -1.00
}
def planet_disk(planet_name, obs, t0, to_sun, earth_sun, return_dict=True):
    """
    obs = between earth and the planet
    sun_dist = between the planet and the sun
    earth_sun = between the earth and sun
    """
    ### Illuminated Fraction of the disk
    d = to_sun.radec()[2].au # planet to sun
    delta = obs.radec()[2].au # earth to planet
    r = earth_sun.radec()[2].au # earth to sun
    #print("R: ", r, "DELTA: ", delta)

    # phase angle
    t1 = (d*d + delta*delta - r*r)
    t2 = 2. * d * delta
    cos_i = t1/t2
    i = math.degrees(math.acos(cos_i))

    # plotting phase angle
    p_lon = obs.ecliptic_latlon()[1].degrees
    s_lon = earth_sun.ecliptic_latlon()[1].degrees
    dl = p_lon - s_lon
    if dl > 180:
        dl = dl - 360 # between -180 and 180.
    plotting_phase = 360 - i if dl < 0. else i

    # illuminated fraction of disk
    k = (cos_i + 1)/2. 

    ### Apparent Magnitude
    if planet_name in MAG.keys():
        mag = MAG[planet_name] + 5 * math.log10(d * delta)
        #print ("M: ", MAG[planet_name], '∆m: ', 5*math.log10(d * delta))
    else:
        mag = None

    # Adjustments to magnitude
    if planet_name == 'Mercury': # due to phase
        mag += 0.380*i - 2.73e-4*i**2 + 2.0e-6*i**3
    elif planet_name == 'Venus': # due to phase
        mag += 9.e-4*i + 2.39e-4*i**2 - 6.5e-7*i**3
    elif planet_name == 'Mars': # due to phase
        mag += 0.016 * i
    elif planet_name == 'Jupiter': # due to phase
        mag += 0.005*i
    elif planet_name == 'Saturn': # due to the tilt of the rings...
        ring = saturn_ring(t0, obs)
        delta_u = ring['i'] # approximation
        bb = math.radians(abs(ring['b']))
        mag += 0.044 * abs(delta_u) - 2.60 * math.sin(bb) + 1.25 * math.sin(bb)**2

    ### Angular Size
    ang_size = get_angular_size(DIAMETERS[planet_name], obs.radec()[2].km) # diameter in arcsec

    return {
        'illum_fraction': k,
        'apparent_mag': mag,
        'phase_angle': i,
        'plotting_phase': plotting_phase,
        'angular_diameter': ang_size
    }

def get_sun(utdt):
    ts = load.timescale()
    t = ts.utc(utdt.year, utdt.month, utdt.day, utdt.hour, utdt.minute)
    objects = load('de421.bsp')
    earth = objects['Earth']
    sun = objects['Sun']
    return earth.at(t).observe(sun)

def get_moon(utdt, apparent=False):
    ts = load.timescale()
    t = ts.utc(utdt.year, utdt.month, utdt.day, utdt.hour, utdt.minute)
    objects = load('de421.bsp')
    earth = objects['Earth']
    moon = earth.at(t).observe(objects['Moon'])
    sun = earth.at(t).observe(objects['Sun'])
    (xmlat, xmlon, xmdist) = moon.ecliptic_latlon()
    (xslat, xslon, xsdist) = sun.ecliptic_latlon()
    moon_lat = xmlat.radians
    moon_lon = xmlon.radians
    sun_lon = xslon.radians
    sun_lat = xslat.radians

    # psi = geocentric elongation
    psi = math.acos(math.cos(moon_lat) * math.cos(moon_lon - sun_lon))

    # i = phase angle
    i_1 = xsdist.au * math.sin(psi)
    i_2 = xmdist.au - xsdist.au * math.cos(psi)
    i = math.atan2(i_1, i_2)

    # chi = position angle of the moon's bright limb
    # Why does Meeus use ecliptic coords and THEN immediately after, use equatorial?
    moon_dec = moon.radec()[1].radians
    moon_ra = moon.radec()[0].radians
    sun_dec = sun.radec()[0].radians
    sun_ra = sun.radec()[0].radians
    chi_1 = math.cos(sun_lat) * math.sin(sun_ra - moon_ra)
    chi_2a = math.sin(sun_dec) * math.cos(moon_dec)
    chi_2b = math.cos(sun_dec) * math.sin(moon_dec) * math.cos(sun_ra - moon_ra)
    chi = math.atan2(chi_1, chi_2a - chi_2b)

    # k = illuminated fraction of the Moon's disk
    k = (1. + math.cos(i)) / 2.

    # magnitude
    """
    Empirically, I get 
        x = log10(k)
        m = -1.146_606*x**2 -5.760_663*x -11.983_484
    """
    x = math.log10(k)
    mag = -1.1466_606*x**2 - 5.760_663*x - 11.983_484

    # angular size
    ang_size = get_angular_size(6378.14, xmdist.km) # diameter in arcsec
    if apparent:
        return moon.radec().apparent()

    return {
        'observe': moon,
        'illum_fraction': k,
        'apparent_mag': mag,
        'angular_diameter': ang_size,
        'phase_angle': i,
        'pos_angle': math.degrees(chi),
        'elongation': math.degrees(psi)
    }


def get_solar_system_object(utdt, name):
    ts = load.timescale()
    t = ts.utc(utdt.year, utdt.month, utdt.day, utdt.hour, utdt.minute)
    t0 = get_t_epoch(get_julian_date(utdt))
    solsys = load('de421.bsp')
    earth = solsys['earth']
    sun = solsys['sun']

    out = {}
    if name not in EPHEMERIS.keys():
        return None

    eph_dict = EPHEMERIS[name]
    target = solsys[eph_dict['p']]
    obs = earth.at(t).observe(target)
    out['observe'] = obs

    # Get solar-system centered values too:
    out['sun'] = target.at(t).observe(sun)
    out['earth_sun'] = earth.at(t).observe(sun)
    out['physical'] = planet_disk(name, out['observe'], t0, out['sun'], out['earth_sun'])

    moon_list = eph_dict['s']
    moon_obs = []
    if moon_list:
        # we have moons!
        moonsys = load(eph_dict['l'])
        earth_s = moonsys['earth']
        for moon in moon_list:
            mdict = {}
            mdict['name'] = moon
            moon_target = moonsys[moon]
            mdict['observe'] = earth_s.at(t).observe(moon_target)
            moon_obs.append(mdict)
    else:
        moon_obs = None
    out['moons'] = moon_obs
    return out

def is_planet_up(utdt, location, ra, dec, min_alt=0.):
    az, alt = get_alt_az(utdt, location.latitude, location.longitude, ra, dec)
    up = alt > min_alt
    return az, alt, up

def get_all_planets(utdt):
    planet_dict = {}
    for name in EPHEMERIS.keys():
        planet = get_solar_system_object(utdt, name)
        planet_dict[name] = planet
    return planet_dict