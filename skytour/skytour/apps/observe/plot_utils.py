
from ..utils.plot import create_plot

STATUS_COLOR = {
	'Active': '#0C0',
	'Possible': '#0FF',
	'Rejected': '#C00',
    'Provisional': '#099',
	'TBD': '#CCC',
	'Issues': '#FC0'
}
MARKER_MAP = {'NY': 'x', 'VT': 'v', 'MA': 'o'}

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

    brightness = []
    travel = []
    sqm = []
    distance = []
    colors = []
    markers = []

    for obj in obj_list:
        sqm.append(obj.sqm)
        travel.append(obj.travel_time)
        brightness.append(obj.brightness)
        distance.append(obj.travel_distance)
        colors.append(STATUS_COLOR[obj.status])
        markers.append(MARKER_MAP[obj.state])

    if type == 'sqm':
        x = distance
        y = sqm
        title = 'SQM by Distance'
        xtitle = 'Distance (miles)'
        ytitle = 'SQM'
        ypad = -0.02

    elif type == 'bright':
        x = travel
        y = brightness
        title = 'Brightness by Travel Time'
        xtitle = 'Travel Time (minutes)'
        ytitle = 'Brightness'

    else:
        x = [0, 1]
        y = [0, 1]
        colors = ['#000', '#000']
        markers = ['o', 'o']

    image = create_plot(
        x = x, y = y, 
        markers = markers, colors = colors,
        grid = grid, title=title,
        xtitle = xtitle, ytitle=ytitle,
        xpad = xpad, ypad = ypad
    )
    return image
