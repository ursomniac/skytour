import io
import base64
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
from .plot_utils import do_scatter_plot, fix_axis

def create_plot(
		type = 'scatter', x = [], y = [], \
		title='Generic Title', xtitle='X Axis', ytitle='Y Axis', \
		colors = None, markers = None, \
		grid = False, \
		xpad = 0., ypad= 0.02, 
		subplot = (1,1,1)
	):
	# Create a new figure
	fig = Figure()
	if subplot:
		panel = fig.add_subplot(subplot[0], subplot[1], subplot[2])
	panel.set_title(title)
	panel.set_xlabel(xtitle)
	panel.set_ylabel(ytitle)
	# Options
	if grid:
		panel.grid()

	panel.set_xlim(fix_axis(x, xpad))
	panel.set_ylim(fix_axis(y, ypad))

	if not type or type == 'scatter':
		panel = do_scatter_plot(panel, x, y, markers, colors)

	# Convert to a PNG image
	pngImage = io.BytesIO()
	FigureCanvas(fig).print_png(pngImage)
	# Encode PNG to Base64 string
	pngImageB64String = 'data:image/png;base64,'
	pngImageB64String += base64.b64encode(pngImage.getvalue()).decode('utf8')
	return pngImageB64String
