import math
from skytour.apps.astro.time import get_julian_date

def get_all_system_longitude(utdt):
    """
    TEST: 
        From https://www.projectpluto.com/grs_form.htm
        This is just to test the mapping.
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