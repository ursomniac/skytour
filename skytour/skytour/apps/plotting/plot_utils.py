### These just abstract things for scatter plots.

def fix_axis(a, pad, ymin = None, ymax = None):
	amin = min(a) if ymin is None or min(a) < ymin else ymin
	amax = max(a) if ymax is None or max(a) > ymax else ymax

	da = amax - amin
	apad = abs(pad)
	rev = pad < 0.
	a_high = amax + da * apad
	a_low = amin - da * apad
	if rev:
		return (a_high, a_low)
	return (a_low, a_high)

def do_scatter_plot(panel, x, y, markers, colors, sizes, reversed=False):
	# Put each point on the plot with the appropriate color and marker

	n = len(x)
	marker_color = '#999' if reversed else '#000'
	markers = n * ['o'] if not markers else markers
	colors = n * [marker_color] if not colors else colors
	sizes = n * [30] if not sizes else sizes
	
	for _x, _y, _c, _m, _s in zip(x, y, colors, markers, sizes):
		panel.scatter(_x, _y, marker=_m, s=_s, c=_c)

	"""
	if markers and colors:
		for _s, _c, _x, _y in zip(markers, colors, x, y):
			panel.scatter(_x, _y, marker=_s, c=_c)
	elif markers and not colors:
		for _s, _x, _y in zip(markers, x, y):
			panel.scatter(_x, _y, marker=_s)
	elif colors and not markers:
		for _c, _x, _y in zip(colors, x, y):
			panel.scatter(_x, _y, c=_c)
	else: 
		for _x, _y in zip(x, y):
			panel.scatter(_x, _y)
	"""
	return panel