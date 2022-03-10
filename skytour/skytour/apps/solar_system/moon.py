from .utils import get_phase_description

def simple_lunar_phase(jd):
    """
    This just does a quick-and-dirty estimate of the Moon's phase given the date.
    """
    lunar_period = 29.530588853
    lunations = (jd - 2451550.1) / lunar_period
    percent = lunations - int(lunations)
    phase_angle = percent * 360.
    delta_t = phase_angle * lunar_period / 360.
    moon_day = int(delta_t + 0.5)
    phase = get_phase_description(phase_angle)

    return {
        'angle': phase_angle, 
        'day': moon_day, 
        'phase': phase, 
        'days_since_new_moon': delta_t
    }
