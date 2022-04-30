import numpy as np
import datetime, pytz
from ..plotting.scatter import create_plot

"""
This is the code to make the two scatter plots on the ObservingLocationList view
"""
STATUS_COLOR = {
	'Active': '#090',
	'Possible': '#0CC',
	'Rejected': '#C00',
    'Provisional': '#00F',
	'TBD': '#CCC',
	'Issues': '#FC0'
}

SIZES = {
    'Active': 100,
	'Possible': 60,
	'Rejected': 20,
    'Provisional': 80,
	'TBD': 50,
	'Issues': 40
}

def make_location_plot(
    obj_list,
    type, 
    title='Generic Title', 
    xtitle = 'X Axis Title',
    ytitle = 'Y Axis Title',
    xpad = 0.02,
    ypad = 0.02,
    grid = True,
):
    """
    This is an attempt to make it easy to make scatter plots...
    """

    brightness = []
    travel = []
    sqm = []
    distance = []
    colors = []
    markers = []
    sizes = []

    for obj in obj_list:
        sqm.append(obj.sqm)
        travel.append(obj.travel_time)
        brightness.append(obj.brightness)
        distance.append(obj.travel_distance)
        colors.append(STATUS_COLOR[obj.status])
        markers.append(obj.state.marker)
        sizes.append(SIZES[obj.status] * .5)

    if type == 'sqm':
        x = distance
        y = sqm
        title = 'SQM by Distance'
        xtitle = 'Distance (miles)'
        ytitle = 'SQM'
        ypad = -0.02
        lines = [20.49, 21.69, 21.89, 21.99]

    elif type == 'bright':
        x = travel
        y = brightness
        title = 'Brightness by Travel Time'
        xtitle = 'Travel Time (minutes)'
        ytitle = 'Brightness'
        lines = [0.685, 0.225, 0.187, 0.171]

    else:
        x = [0, 1]
        y = [0, 1]
        colors = ['#000', '#000']
        markers = ['o', 'o']

    image = create_plot(
        x = x, y = y, 
        markers = markers, colors = colors, sizes=sizes,
        grid = grid, title=title,
        xtitle = xtitle, ytitle=ytitle,
        xpad = xpad, ypad = ypad,
        lines = lines
    )
    return image

def plot_sqm_history(loc):
    sessions = loc.observingsession_set.all()
    if sessions.count() < 1:
        return None
    lines = [loc.sqm] if loc.sqm is not None else []
    x = []
    y = []
    e = []

    for s in sessions:
        sx = s.ut_date
        sy = []
        obs = s.observingcircumstances_set.all()
        for o in obs:
            if o.sqm is not None:
                sy.append(o.sqm)
        if len(sy) == 0:
            continue
        avg = np.average(sy)
        rms = np.std(sy)
        x.append(sx)
        y.append(avg)
        e.append(rms)

    if len(x) > 0 and len(y) > 0:
        image = create_plot(
            x=x, 
            y=y, 
            grid=True, 
            error=e, 
            lines=lines, 
            xpad=0., 
            ypad=-0.02,
            title=f"SQM Measures: {loc}",
            xtitle='Date',
            ytitle='SQM (mag/arcsec^2)'
        )
        return image
    return None