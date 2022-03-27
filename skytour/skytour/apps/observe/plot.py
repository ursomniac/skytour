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

    for obj in obj_list:
        sqm.append(obj.sqm)
        travel.append(obj.travel_time)
        brightness.append(obj.brightness)
        distance.append(obj.travel_distance)
        colors.append(STATUS_COLOR[obj.status])
        markers.append(obj.state.marker)

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
        markers = markers, colors = colors,
        grid = grid, title=title,
        xtitle = xtitle, ytitle=ytitle,
        xpad = xpad, ypad = ypad,
        lines = lines
    )
    return image
