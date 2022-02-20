import datetime, pytz
from skyfield.api import load 
from skyfield.almanac import phase_angle as get_phase_angle, fraction_illuminated
from skyfield.magnitudelib import planetary_magnitude
from ..observe.almanac import get_object_rise_set
from ..observe.local import get_observing_situation
from ..utils.compile import observe_to_values
from ..utils.format import to_sex
from .jupiter import get_jupiter_physical_ephem
from .mars import get_mars_physical_ephem
from .utils import (
    get_angular_size, 
    get_plotting_phase_angle, 
    get_elongation,
    get_constellation,
)
from .vocabs import PLANETS

def get_solar_system_object(utdt, planet, utdt_end=None, location=None):
    """
    For a given UTDT get all the metadata for a planet of the given name.

    This returns a dict with - basically - everything.

    Options: 
        - location - the ObservingLocation record
            If provided, then almanac information (rise/set) will be added
        - utdt_end - the ending of the observing window
            If provided (with location) then alt/az info at start/end will be added.
    """
    # Things from Skyfield to get things started.
    ts = load.timescale()
    t = ts.utc(utdt.year, utdt.month, utdt.day, utdt.hour, utdt.minute)
    eph = load('de421.bsp')
    earth = eph['earth']

    # Get the coordinates at time t from Earth
    obs = earth.at(t).observe(eph[planet.target])
    (obs_ra, obs_dec, obs_distance) = obs.radec()
    ra = obs_ra.hours.item()
    dec = obs_dec.degrees.item()
    # Get what constellation this is in
    constellation = get_constellation(obs_ra.hours.item(), obs_dec.degrees.item())
    # Get the location of the Sun (from Earth)
    sun = earth.at(t).observe(eph['sun'])
    
    # If location is provided, get the almanac dict
    almanac = get_object_rise_set(utdt, eph, eph[planet.target], location) if location else None
    # if location AND utdt_end are provided, get the session dict
    session = get_observing_situation(ra, dec, utdt, utdt_end, location) if utdt_end and location else None

    # Get things from almanac
    # i = phase angle
    i = get_phase_angle(eph, planet.target, t).degrees.item() # degrees
    ang_size = get_angular_size(planet.diameter, obs.radec()[2].km) # diameter in arcsec
    elongation = get_elongation(obs, sun)
    # This generates an angle to use for plotting the planet's disk.
    # It (clumsily) handles the difference between inferior planets and the Moon.
    plotting_phase_angle = get_plotting_phase_angle(planet.name, i, elongation)
    # k = illuminated fraction of the Moon's disk
    k = fraction_illuminated(eph, planet.target, t).item() # float

    # apparent magnitude
    try:
        mag = planetary_magnitude(obs).item()
    except:
        mag = None # there are some edge issues...

    # deal with moons
    # This is the list of moons that we're following
    moon_list = planet.moon_list
    moon_obs = []
    if moon_list:
        # we have moons!
        # Load up the partial elements (only good to 2030 - remember to generate a new one...)
        moonsys = load(planet.load)
        earth_s = moonsys['earth']
        # For each moon, get the coordinates (as a dict) and add it to a list of moons.
        for moon in moon_list:
            mdict = {}
            mdict['name'] = moon
            moon_target = moonsys[moon]
            mdict['target'] = earth_s.at(t).observe(moon_target)
            moon_obs.append(mdict)
    else: # No moons
        moon_obs = None

    # Special things for planets:
    physical = None
    if planet.name == 'Jupiter':
        physical = get_jupiter_physical_ephem(utdt, planet)
    elif planet.name == 'Mars':
        physical = get_mars_physical_ephem(utdt, planet)

    return {
        'name': planet.name,
        'object': planet,
        'slug': planet.slug,
        'target': obs,
        'coords': observe_to_values(obs),
        'observe': {
            'constellation': constellation,
            'illum_fraction': k * 100.,  # percent
            'apparent_mag': mag,
            'angular_diameter': ang_size,
            'angular_diameter_str': to_sex(ang_size/3600., format='degrees'),
            'phase_angle': i,
            'phase_angle_str': to_sex(i, format="degrees"),
            'plotting_phase_angle':  plotting_phase_angle,
            'elongation': elongation
        },
        'physical': physical,
        'close_to': [], # will fill in downstream
        'almanac': almanac,
        'session': session,
        'moons': moon_obs
    }


def get_ecliptic_positions(utdt=None):
    if utdt is None:
        utdt = datetime.datetime.utcnow().replace(tzinfo=pytz.utc)
    all_planets = PLANETS
    all_planets.insert(2, 'Earth')
    # start
    ts = load.timescale()
    t = ts.utc(utdt.year, utdt.month, utdt.day, utdt.hour, utdt.minute)
    eph = load('de421.bsp')
    sun = eph['sun']
    points = []
    for planet in all_planets:
        loc = planet.upper() + ' BARYCENTER'
        coords = sun.at(t).observe(eph[loc])
        latitude, longitude, distance = coords.ecliptic_latlon()
        d = dict(
            name=planet,
            longitude=longitude.degrees.item(),
            latitude=latitude.degrees.item(),
            distance=distance.au.item()
        )
        points.append(d)
    return points

    
