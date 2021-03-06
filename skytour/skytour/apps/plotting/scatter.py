import io
import base64
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib import pyplot as plt
from matplotlib.figure import Figure
from .plot_utils import do_scatter_plot, fix_axis

def create_plot(
        type = 'scatter', 
        x = [], 
        y = [],
        title='Generic Title', 
        xtitle='X Axis', 
        ytitle='Y Axis',
        colors = None, 
        markers = None, 
        lines = None,
        sizes = None,
        grid = False,
        error = None,
        xpad = 0., 
        ypad = 0.02, 
        ylim = None,
        subplot = (1,1,1),
        reversed = False
	):
    """
    Given data, make a scatter plot.
    """
	# Create a new figure
    #style = 'dark_background' if reversed else 'default'
    fig = Figure()
    #plt.style.use(style)

    if subplot:
        panel = fig.add_subplot(subplot[0], subplot[1], subplot[2])
    
    panel.set_title(title)
    panel.set_xlabel(xtitle)
    panel.set_ylabel(ytitle)
    # Options
    if grid:
        panel.grid()

    panel.set_xlim(fix_axis(x, xpad))
    panel.set_ylim(fix_axis(y, ypad, ymax=ylim))
    if not type or type == 'scatter':
        panel = do_scatter_plot(panel, x, y, markers, colors, sizes, reversed=reversed)
        if error:
            panel.errorbar(x, y, yerr=error, linestyle='None')

    if lines and len(lines) > 0:
        ltype = ['--', '-.']
        ll = 0
        for line in lines:
            panel.axhline(line, ls = ltype[ll % len(ltype)], color='#333')
            ll += 1

    # Convert to a PNG image
    pngImage = io.BytesIO()
    FigureCanvas(fig).print_png(pngImage)
    # Encode PNG to Base64 string
    pngImageB64String = 'data:image/png;base64,'
    pngImageB64String += base64.b64encode(pngImage.getvalue()).decode('utf8')

    plt.cla()
    plt.close(fig)
    
    return pngImageB64String

def create_histogram(x, y):
    pass