import math
import numpy as np
from datetime import datetime, timezone, timedelta
from skyfield.api import load #, wgs84

def saturn_ring(t, pdict):
    """
    Given the obs object for Saturn, get ring information.
    """
    # Saturn's position (provided)
    ecl_lat = pdict['apparent']['ecl']['latitude']
    ecl_lon = pdict['apparent']['ecl']['longitude']
    distance = pdict['apparent']['distance']['au']

    lamb = math.radians(ecl_lon)
    beta = math.radians(ecl_lat)

    # inclination of the plane of the ring
    iota = math.radians(28.075_216 - 0.012_998*t + 4.e-6*t**2)
    # longitude of the ascending node
    omega = math.radians(169.508_470 + 1.394_681*t + 4.12e-4*t**2)
    
    bb = math.asin(
        math.sin(iota) * math.cos(beta) * math.sin(lamb - omega) \
            - math.cos(iota) * math.sin(beta)
    )
    # Major and minor axes of the rings in arcseconds
    a = 375.35 / distance # geo_dist in AU;  arcsec
    b = a * math.sin(abs(bb))
    # inner ring  a, b * 0.665
    # outer ring  a, b * ?
    
    # TODO V2.x: factor in the tilt of the axis projected to the earth
    # Longitude of the ascending node of Saturn's orbit
    # n = 113.6655 + 0.8771 * t  # degrees

    return {
        'major': a,
        'minor': b,
        'i': math.degrees(iota),
        'b': math.degrees(bb)
    }


import numpy as np
from skyfield.api import load
from skyfield.magnitudelib import planetary_magnitude

# Setup: Load ephemeris once (de421.bsp contains Saturn/Iapetus)


def get_iapetus_magnitude(utc_datetime=None, debug=False):
    """
    Calculates Iapetus's apparent magnitude for a given datetime object.
    Accounts for: distance to Sun/Earth, phase angle, and orbital position (albedo).
    """
    eph = load('generated_data/sat_excerpt.bsp')
    sun, earth, saturn = eph['sun'], eph['earth'], eph['saturn barycenter']
    iapetus = eph['iapetus']
    ts = load.timescale()
    # 1. Convert datetime to Skyfield time
    # Handles microseconds/seconds as float automatically
    if utc_datetime is None:
        utc_datetime = datetime.now(datetime.timezone.utc)
    t = ts.utc(utc_datetime.year, utc_datetime.month, utc_datetime.day, 
               utc_datetime.hour, utc_datetime.minute, 
               utc_datetime.second + utc_datetime.microsecond / 1e6)

    # 2. Get positions and distances
    astrometric = earth.at(t).observe(iapetus)
    r_sun = sun.at(t).observe(iapetus).distance().au
    delta_earth = astrometric.distance().au
    
    # 3. Base Magnitude (H) + Distance Correction
    # H = 1.65 is a mean absolute magnitude for Iapetus
    # Formula: m = H + 5*log10(r * delta)
    h_mean = 1.65
    mag_dist = h_mean + 5 * np.log10(r_sun * delta_earth)
    
    # 4. Phase Angle Correction (Sun-Iapetus-Earth angle)
    # Simple linear approximation for small phase angles common for Saturn
    #phase_angle = astrometric.phase_angle().degrees
    phase_angle = astrometric.phase_angle(sun).degrees

    mag_phase = 0.04 * phase_angle 
    
    # 5. Orbital Variation (The "Iapetus Effect")
    # Leading hemisphere (dark) is visible at Eastern Elongation (~90°)
    # Trailing hemisphere (bright) is visible at Western Elongation (~270°)
    v_sun_sat = saturn.at(t).position.au - sun.at(t).position.au
    v_sat_iap = iapetus.at(t).position.au - saturn.at(t).position.au
    
    # Calculate orbital longitude relative to the Sun-Saturn line
    dot = np.dot(v_sun_sat, v_sat_iap)
    cross = np.linalg.norm(np.cross(v_sun_sat, v_sat_iap))
    orbit_angle = np.degrees(np.arctan2(cross, dot))
    
    # Sinusoidal albedo variation (Amplitude ~0.85 mag, total swing ~1.7)
    # Brightest at 270 degrees
    mag_albedo = 0.85 * np.cos(np.radians(orbit_angle - 270))
    
    return mag_dist + mag_phase + mag_albedo

def test_iapetus_magnitude(n=30, base=None, offset=3.):
    if base is None:
        base = datetime.now(timezone.utc)
    for i in range(n):
        m = get_iapetus_magnitude(base)
        print(f"UT: {base} Mag: {m}")
        base = base + timedelta(days=offset)

