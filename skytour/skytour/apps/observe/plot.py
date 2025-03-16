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
    reversed = False
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
        if obj.state is not None:
            markers.append(obj.state.marker)
        else:
            markers.append('x')
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
        lines = lines,
        reversed = reversed
    )
    return image

def plot_expect_vs_observed_sqm(locations, reversed=False):
    xx = []
    yy = []
    ee = []
    for loc in locations:
        (y, e) = loc.mean_obs_bortle
        if y is None:
            continue
        x = loc.effective_bortle
        e = 0.0 if e is None else e
        xx.append(x)
        yy.append(y)
        ee.append(e)
    image = create_plot(
            x = xx, y = yy, 
            xpad=0.02, ypad=0.02,
            error = ee, grid=True,
            xrange = [min(2.9, min(xx)), max(5, max(xx))],
            yrange = [min(4, min(yy)), max(6, max(yy))],
            other_lines = [([3, 6], [3, 6]),],
            title='Obs. Bortle vs. Expected',
            reversed=reversed
        )
    return image

def plot_sqm_history(loc, reversed=False):
    sessions = loc.observingsession_set.all()
    if sessions.count() < 1:
        return None
    sqm = loc.sqm if loc.sqm is not None else None
    lines = [loc.sqm] if loc.sqm is not None else []
    x_use = []
    y_use = []
    e_use = []
    s_use = []
    c_use = []
    y_use_total = 0.
    x_ignore = []
    y_ignore = []
    e_ignore = []
    s_ignore = []
    c_ignore = []
    y_ignore_total = 0.

    marker_color = '#999' if reversed else '#000'

    for s in sessions:
        sx = s.ut_date
        sy = []
        si = []
        obs = s.observingcircumstances_set.all()
        for o in obs:
            if o.sqm is not None and o.use_sqm:
                sy.append(o.sqm)
            elif o.sqm is not None and not o.use_sqm:
                si.append(o.sqm)
        if len(sy) > 0:            
            avg = np.average(sy)
            rms = np.std(sy)
            x_use.append(sx)
            y_use.append(avg)
            y_use_total += avg
            e_use.append(rms)
            s_use.append('o')
            c_use.append(marker_color)
        if len(si) > 0:
            avg = np.average(si)
            rms = np.std(si)
            x_ignore.append(sx)
            y_ignore.append(avg)
            y_ignore_total += avg
            e_ignore.append(rms)
            s_ignore.append('x')
            c_ignore.append('#f00')
        #print(f"X: {sx}  Y: {avg}  E: {rms}")

    x_all = x_use + x_ignore
    y_all = y_use + y_ignore
    e_all = e_use + e_ignore
    s_all = s_use + s_ignore
    c_all = c_use + c_ignore

    if len(x_use) > 0 and len(y_use) > 0:
        sqm_avg = y_use_total / len(y_use)
        lines.append(sqm_avg)
        image = create_plot(
            x=x_all, 
            y=y_all, 
            grid=True, 
            error=e_all, 
            lines=lines, 
            markers=s_all,
            colors=c_all,
            xpad=0.1, 
            ypad=-0.2,
            ylim = sqm,
            title=f"SQM Measures: {loc}",
            xtitle='Date',
            ytitle='SQM (mag/arcsec^2)',
            reversed=reversed
        )
        return image
    return None