def fix_axis(a, pad):
	da = max(a) - min(a)
	apad = abs(pad)
	rev = pad < 0.
	a_high = max(a) + da * apad
	a_low = min(a) - da * apad
	if rev:
		return (a_high, a_low)
	return (a_low, a_high)

def do_scatter_plot(panel, x, y, markers, colors):
	# Put each point on the plot with the appropriate color and marker
	# UGH - I don't know how to handle the combinations elegantly.
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
	return panel