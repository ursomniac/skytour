
from .transform import get_alt_az

def is_object_up(utdt, location, ra, dec, min_alt=0.):
    """
    Given:
        1. RA, Dec of an object
        2. UTDT and Location object
        return a boolean if those coordinates are above the horizon
        at that time/location.

    You can customize with a minimum altitude (default = 0.0°)
    """
    az, alt, airmass = get_alt_az(utdt, location.latitude, location.longitude, ra, dec)
    up = alt > min_alt
    return az, alt, up, airmass

def get_observing_situation(ra, dec, utdt_start, utdt_end, location):
    """
    Given:
        1. ra, dec
        2. UT values
        3. location
    Get the altitude, azimuth, and a flag is_up for each UT.
    Return as a dict where the key is "start"/"end" (for the observing session).
    """
    d = {}
    for k, v in [('start', utdt_start), ('end', utdt_end)]:
        d[k] = {}
        az, alt, is_up, airmass = is_object_up(v, location, ra, dec, min_alt=0.)
        d[k]['azimuth'] = az
        d[k]['altitude'] = alt
        d[k]['is_up'] = is_up
        d[k]['airmass'] = airmass
    return d
