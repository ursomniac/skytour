from dateutil.parser import isoparse

def get_initial_from_cookie(up):
    utdt_start = isoparse(up['utdt_start'])
    date = utdt_start.date()
    time = utdt_start.time()
    initial = dict(
        date = date,
        time = time,
        session_length = up.get('session_length',3),
        mag_limit = up.get('mag_limit', 12.),
        hour_angle_range = up.get('hour_angle_range', 3.5),
        show_planets = up.get('show_planets', 'visible'),
        location=up['location']
    )
    return initial