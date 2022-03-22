import math
from skyfield.almanac import moon_phase
from skyfield.api import load
from skyfield.magnitudelib import planetary_magnitude
from ..observe.almanac import get_object_rise_set
from ..observe.local import get_observing_situation

from .comets import get_comet_target
from .jupiter import get_jupiter_physical_ephem
from .mars import get_mars_physical_ephem
from .moon import simple_lunar_phase, equ_lunar_phase_angle
from .serializer import serialize_astrometric
from .utils import (
    get_angular_size,
    get_angular_size_string,
    get_plotting_phase_angle,
    get_constellation,
    get_elongation,
    get_meeus_phase_angle
)

def get_object_metadata(
        utdt, 
        eph_label, 
        object_type, 
        utdt_end=None, 
        instance=None, 
        location=None,
        time_zone=None
    ):
    """
    Get the serialized metadata for an object at a given utdt and location.
        1. UTDT
        2. eph_label = the string for eph
        3. object_type = moon|planet|asteroid|comet
        4. Instance = the model Instance
        5. Location = observing location
    """
    ts = load.timescale()
    t = ts.utc(utdt)
    jd = t.tt.item()

    eph = load('de421.bsp')
    earth = eph['Earth']
    sun = eph['Sun']
    if object_type == 'comet':
        if instance is None:
            return None
        eph_body, row = get_comet_target(instance, ts, sun)
    elif object_type == 'asteroid':
        if instance is None:
            return None
        # TODO: This is a hack, really but it improves processing by 20%
        eph_body = eph_label
    else: 
        eph_body = eph[eph_label]

    # Earth-Object
    try:
        target = earth.at(t).observe(eph_body).apparent() # for solar system objects
    except:
        print(f"Cannot establish target {eph_body} - skipping")
        return None
    apparent = serialize_astrometric(target)
    r_earth_target = apparent['distance']['au'] # Earth-Target distance
    # Sun-Object
    sun_target = sun.at(t).observe(eph_body) # sun to target
    r_sun_target = sun_target.radec()[2].au.item()
    apparent['sun_distance'] = r_sun_target
    # Earth-Sun
    sun_apparent = serialize_astrometric(earth.at(t).observe(sun).apparent())
    r_earth_sun = sun_apparent['distance']['au']

    # Shortcuts for things we'll need
    ra = apparent['equ']['ra']
    dec = apparent['equ']['dec']
    longitude = apparent['ecl']['longitude']
    sun_long = sun_apparent['ecl']['longitude']

    # Get rise/set and session parameters
    almanac = get_object_rise_set(utdt, eph, eph_body, location, serialize=True, time_zone=time_zone) if location else None
    session = get_observing_situation(ra, dec, utdt, utdt_end, location) if utdt_end and location else None

    # Special Cases --- ADD to observe dict
    if object_type == 'moon':
        lunar_phase = simple_lunar_phase(jd) # this is a DICT!
        position_angle = moon_phase(eph, t).degrees.item() # degrees

    ### Observational Metadata:
    # Constellation
    constellation = get_constellation(ra, dec)

    # Elongation - this is just target.longitude - sun.longitude
    elongation = get_elongation(longitude, sun_long)

    # Phase Angle and phase
    # For some reason this gives the wrong answer.
    #if object_type in ['comet', 'asteroid']:
    #    cos_beta = (r_sun_target**2 + r_earth_target**2 - r_earth_sun**2)/(2. * r_sun_target * r_earth_target)
    #    # For some reason this doesn't always work.
    #    if abs(cos_beta) <= 1.:
    #        phase_angle = math.degrees(math.acos(cos_beta))
    #    else:
    #        phase_angle = None
    #else:
    #    skyfield_phase_angle = get_phase_angle(eph, eph_label, t).degrees.item() # degrees

    if object_type == 'sun':
        phase_angle = 0.
    elif object_type == 'moon':
        phase_angle = equ_lunar_phase_angle(apparent, sun_apparent, r_earth_sun, r_earth_target)
    else:
        phase_angle = meeus_phase_angle = get_meeus_phase_angle(r_earth_sun, r_earth_target, r_sun_target) \

    plotting_phase_angle = None
    if object_type == 'planet' and instance is not None:
        plotting_phase_angle = get_plotting_phase_angle(instance.name, phase_angle, elongation)
    elif object_type == 'moon':
        plotting_phase_angle = lunar_phase['angle']

    # Illum. Fraction - in percent
    # TODO: This is never right - why?
    #k = 100. * fraction_illuminated(eph, eph_label, t).item() if object_type in ['moon', 'planet'] else None
    if phase_angle is not None:
        k = 0.5 * (1. + math.cos(math.radians(phase_angle)))
        fraction_illuminated = 100. * k
    else:
        fraction_illuminated = None

    # Apparent Magnitude
    if object_type == 'moon':
        x = math.log10(k)
        mag = -1.1466_606*x**2 - 5.760_663*x - 11.983_484
    elif object_type == 'sun':
        mag = -26.74
    elif object_type == 'planet':
        try:
            mag = planetary_magnitude(target).item()
        except:
            mag = None # there are some edge issues...
    elif object_type == 'asteroid':
        mag = None
        # This is apparently in Skyfield v1.42 as-yet not released.
        if phase_angle:
            rpa = math.radians(phase_angle) # Assuming this is the same phase angle
            phi_1 = math.exp(-3.33 * math.tan(rpa/2.)**0.63)
            phi_2 = math.exp(-1.87 * math.tan(rpa/2.)**1.22)
            m1 = instance.h + 5 * math.log10(r_sun_target * r_earth_target) 
            m2 = 2.5 * math.log10((1 - instance.g) * phi_1 + instance.g * phi_2)
            mag = m1 - m2
    elif object_type == 'comet':
        mg = row['magnitude_g']
        mk = row['magnitude_k']
        mag = mg + 5. * math.log10(r_earth_target) + mk * math.log10(r_sun_target)
    else:
        mag = None
    apparent_magnitude = mag

    # Angular Diameter
    if object_type == 'moon':
        diam = 3_475
    elif object_type == 'sun':
        diam = 1_391_016
    elif object_type == 'earth':
        diam = 12_756
    elif object_type == 'planet' and instance is not None:
        diam = instance.diameter
    elif object_type == 'asteroid' and instance is not None:
        diam = instance.mean_diameter
    else:
        diam = None
    angular_diameter = get_angular_size(diam, apparent['distance']['km']) /3600. if diam else None
    angular_diameter_str = get_angular_size_string(angular_diameter)

    ### Put all of this into an "observe" dict.
    observe = dict (
            constellation = constellation, 
            phase_angle = phase_angle,                   # degrees
            #meeus_phase_angle = meeus_phase_angle,      # degrees
            plotting_phase_angle = plotting_phase_angle, # degrees
            fraction_illuminated = fraction_illuminated, # percent
            elongation = elongation,                     # degrees
            angular_diameter = angular_diameter,         # degrees
            angular_diameter_str = angular_diameter_str,
            apparent_magnitude = apparent_magnitude
        )
    if object_type == 'moon':
        observe['lunar_phase'] = lunar_phase
        observe['position_angle'] = position_angle
        
    # Moons
    moon_obs = None
    if object_type == 'planet' and instance is not None:
        if instance.moon_list:
            moon_obs = []
            moonsys = load(instance.load)
            earth_s = moonsys['earth']
            for moon in instance.moon_list:
                mdict = {}
                mdict['name'] = moon
                moon_target = moonsys[moon]
                obs = earth_s.at(t).observe(moon_target)
                mdict['apparent'] = serialize_astrometric(obs)
                moon_obs.append(mdict)

    # Physical (Mars, Jupiter)
    physical = None
    if object_type == 'planet' and instance is not None:
        if instance.name == 'Jupiter':
            physical = get_jupiter_physical_ephem(utdt, instance)
        elif instance.name == 'Mars':
            physical = get_mars_physical_ephem(utdt, instance)

    return_dict = dict(
            apparent = apparent,
            almanac = almanac,
            session = session,
            observe = observe,
            moons = moon_obs,
            physical = physical
        )
    return return_dict
