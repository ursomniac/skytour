
from ..solar_system.planets import is_planet_up
from ..utils.format import to_sex

def get_observing_situation(obs_dict, utdt_start, utdt_end, location):
    """
    Given:
        1. object location object
        2. UT values
        3. location
    Get the altitude, azimuth, and a flag is_up for each UT.
    """
    d = {}
    (obj_ra, obj_dec, obj_dist) = obs_dict['target'].radec()
    for k, v in [('start', utdt_start), ('end', utdt_end)]:
        d[k] = {}
        az, alt, is_up = is_planet_up(v, location, obj_ra.hours.item(), obj_dec.degrees.item(), min_alt=0.)
        d[k]['azimuth'] = az
        d[k]['altitude'] = alt
        d[k]['is_up'] = is_up
    obs_dict['session'] = d
    return obs_dict
