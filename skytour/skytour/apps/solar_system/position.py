import math
from skyfield.almanac import (
    phase_angle as get_phase_angle, 
    fraction_illuminated,
    moon_phase
)
from skyfield.api import load
from skyfield.magnitudelib import planetary_magnitude
from ..observe.almanac import get_object_rise_set
from ..solar_system.comets import get_comet_target
from .moon import simple_lunar_phase
from .models import Planet, Comet
from .serializer import serialize_astrometric
from .utils import (
    get_angular_size,
    get_constellation
)

def get_object_metadata(utdt, eph_label, object_type, instance=None, location=None):
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
        eph_body, row = get_comet_target(instance, ts, sun)
    else: 
        eph_body = eph[eph_label]

    target = earth.at(t).observe(eph_body).apparent() # for solar system objects
    apparent = serialize_astrometric(target)

    # The Triangle between Earth, the Sun, and the target
    sun_target = sun.at(t).observe(eph_body) # sun to target
    sun_apparent = serialize_astrometric(earth.at(t).observe(sun).apparent())
    earth_sun = earth.at(t).observe(sun)
    r_earth_sun = earth_sun.radec()[2].au.item()

    # Shortcuts for things we'll need
    ra = apparent['equ']['ra']
    dec = apparent['equ']['dec']
    delta = apparent['distance']['au']
    longitude = apparent['ecl']['longitude']
    sun_long = sun_apparent['ecl']['longitude']
    r_sun = sun_target.radec()[2].au.item()

    # Get rise/set
    almanac = get_object_rise_set(utdt, eph, eph_body, location, serialize=True) if location else None

    ### Observational Metadata:
    # Constellation
    constellation = get_constellation(ra, dec)
    # Elongation - this is just target.longitude - sun.longitude
    elongation = longitude - sun_long
    # Phase Angle and phase
    if object_type == 'comet':
        cos_beta = (r_sun**2 + delta*+2 - r_earth_sun**2)/(2. * r_earth_sun * delta)
        # For some reason this doesn't always work.
        if abs(cos_beta) <= 1.:
            phase_angle = math.degrees(math.acos(cos_beta))
        else:
            phase_angle = None
    else:
        phase_angle = get_phase_angle(eph, eph_label, t).degrees.item() # degrees
    # Illum. Fraction if Moon/Mercury/Venus
    k = 1
    if eph_label.lower() in ['moon', 'mercury', 'venus', 'mars']:
        k = fraction_illuminated(eph, eph_label, t).item() # float
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
        # This is apparently in Skyfield v1.42 as-yet not released.
        rpa = math.radians(phase_angle) # Assuming this is the same phase angle
        phi_1 = math.exp(-3.33 * math.tan(rpa/2.)**0.63)
        phi_2 = math.exp(-1.87 * math.tan(rpa/2.)**1.22)
        m1 = instance.h + 5 * math.log10(r_sun * delta) 
        m2 = 2.5 * math.log10((1 - instance.g) * phi_1 + instance.g * phi_2)
        mag = m1 - m2
    elif object_type == 'comet':
        g = row['magnitude_g']
        k = row['magnitude_k']
        mag = g + 5. * math.log10(delta) + k * math.log10(r_sun)
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
        diam = 0.
    angular_diameter = get_angular_size(diam, apparent['distance']['km'])


    ### Put all of this into an "observe" dict.
    observe = dict (
            constellation = constellation, 
            phase_angle = phase_angle,                # degrees
            fraction_illuminated = k * 100.,          # percent
            elongation = elongation,                  # degrees
            angular_diameter = angular_diameter,      # arcseconds
            apparent_magnitude = apparent_magnitude
        )
    # Special Cases --- ADD to observe dict
    if object_type == 'moon':
        observe['lunar_phase'] = simple_lunar_phase(jd) # this is a DICT!
        observe['position_angle'] = moon_phase(eph, t).degrees.item() # degrees

    return_dict = dict(
            apparent = apparent,
            almanac = almanac,
            observe = observe
        )

    # Planetary Satellites!!!


    return return_dict

def get_planet_positions(utdt, location=None):
    """
    This replaces the get_planet_dict (eventually)
    """
    planets = Planet.objects.order_by('pk')
    planet_dict = {}
    for p in planets:
        d = get_object_metadata(utdt, p.target, 'planet', instance=p, location=location)
        d['slug'] = p.slug
        d['name'] = p.name
        planet_dict[p.name] = d
        # Deal with moons!
    return planet_dict

def get_comet_positions(utdt, location=None):
    comets = Comet.objects.filter(status=1)
    comet_list = []
    for c in comets:
        d = get_object_metadata(utdt, c.name, 'comet', instance=c, location=location)
        d['pk'] = c.pk
        d['name'] = c.name
        comet_list.append(d)
    return comet_list
