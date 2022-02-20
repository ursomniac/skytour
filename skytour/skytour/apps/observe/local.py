
from ..utils.transform import get_alt_az

def is_object_up(utdt, location, ra, dec, min_alt=0.):
    az, alt = get_alt_az(utdt, location.latitude, location.longitude, ra, dec)
    up = alt > min_alt
    return az, alt, up

def get_observing_situation(ra, dec, utdt_start, utdt_end, location):
    """
    Given:
        1. ra, dec
        2. UT values
        3. location
    Get the altitude, azimuth, and a flag is_up for each UT.
    """
    d = {}
    #(obj_ra, obj_dec, obj_dist) = obs.radec()
    for k, v in [('start', utdt_start), ('end', utdt_end)]:
        d[k] = {}
        az, alt, is_up = is_object_up(v, location, ra, dec, min_alt=0.)
        d[k]['azimuth'] = az
        d[k]['altitude'] = alt
        d[k]['is_up'] = is_up
    return d
