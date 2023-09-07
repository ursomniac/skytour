from ..observe.models import ObservingLocation
from ..site_parameter.helpers import find_site_parameter

TIMES_TO_RUN = {'8 PM': -4, '10 PM': -2, '12 AM': 0, '2 AM': 2}
def make_observing_date_grid(dso):
    # TODO: Make this use the cookie, if available
    grid = {}
    no_grid_reason = None
    delta_days, cos_hh = dso.hour_angle_min_alt
    if delta_days is None:
        no_grid_reason = 'Circumpolar' if cos_hh < 0 else 'Too far South'
        opposition_date = None
    else:
        opposition_date = dso.opposition_date
        for k, v in TIMES_TO_RUN.items():
            d1, d2 = dso.shift_observing_dates(delta=v)
            dz = dso.shift_opposition_date(delta=v)
            grid[k] = (d1, dz, d2)
    return dict(opp = opposition_date, grid = grid, no_grid_reason=no_grid_reason)
    
def get_max_altitude(dso, location=None):
    if location is None: # Get the default location
        location_id = find_site_parameter('default-location-id', param_type=int, default=1)
        location = ObservingLocation.objects.get(pk=location_id)
    lat = location.latitude
    delta = 90. - lat + dso.dec
    delta = 180 - delta if delta > 90 else delta
    return delta