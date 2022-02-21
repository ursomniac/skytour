import base64
import datetime, pytz
import io
import math
import numpy as np
import time

from matplotlib import pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.collections import LineCollection
from matplotlib import patches

from skyfield.api import Star, load
from skyfield.data import hipparcos, mpc, stellarium
from skyfield.projections import build_stereographic_projection

from ..plotting.map import *
from ..session.cookie import deal_with_cookie
from ..site_parameter.helpers import find_site_parameter
from ..stars.models import BrightStar
from .models import DSO

def plot_dso(ax, x, y, dso, color='r', reversed=True, size_limit=0.0005, alpha=1):

    oangle = dso.orientation_angle or 0
    ft = dso.object_type.map_symbol_type

    # Get the major/minor axis sizes
    aminor = dso.minor_axis_size # total width
    amajor = dso.major_axis_size # total length
    if aminor == 0:
        aminor = amajor
    ratio = aminor / amajor
    if amajor > 60.:
        amajor = 60
        aminor = ratio * amajor
    if amajor < 3.:
        amajor = 3
        aminor = ratio * amajor
    #print (f"AMAJOR: {amajor} AMINOR: {aminor}")
    amajor *= 2.909e-4
    aminor *= 2.909e-4
    # 2.909e-4
    #angle = 90 - oangle
    angle = oangle

    #if amajor < size_limit or aminor < size_limit: # if it's too small put the marker there instead
    #    ft = 'marker'

    #('marker', 'Marker'),                               # default - star like things, or unknown
    #('ellipse', 'Ellipse'),                             # galaxies - maybe not irregular
    #('open-circle', 'Open Circle'),                     # open clusters, associations
    #('gray-circle', 'Gray Circle'),                     # globular clusters
    #('circle-square', 'Circle in Square'),              # planetary nebulae
    #('square', 'Open Square'),                          # Emission Nebulae
    #('gray-square', 'Gray Square'),                     # Dark Nebulae
    #('circle-gray-square', 'Circle in Gray Square')     # cluster w/ nebulosity
    #print (f'{ft}: X: {x:.3f} Y: {y:.3f}    A: {amajor:.4f}  B: {aminor:.4f}  O: {angle:3d} T: {alpha:.1f}')
    if ft == 'ellipse': # galaxies
        color = '#63f' if 'barred' in dso.object_type.slug.lower() else '#f00'
        e1 = patches.Ellipse((x, y), aminor, amajor, angle=angle, fill=True, color=color, alpha=alpha)
        e2 = patches.Ellipse((x, y), aminor, amajor, angle=angle, fill=False, color='#999')
        ax.add_patch(e1)
        ax.add_patch(e2)
    elif ft in ['open-circle', 'gray-circle', 'circle-plus']: # clusters
        color = '#999' if ft == 'gray-circle' else '#ff0'
        c1 = patches.Circle((x, y), amajor/2., fill=True, color=color, alpha=alpha)
        c2 = patches.Circle((x, y), amajor/2., fill=False, color='#000')
        if ft == 'circle-plus':
            ax.vlines(x, y-amajor/2, y+amajor/2, color='k')
            ax.hlines(y, x-amajor/2, x+amajor/2, color='k')
        ax.add_patch(c1)
        ax.add_patch(c2)
    elif ft in ['square', 'gray-square', 'circle-square', 'circle-gray-square']: # UGH - the center point is the lower-left corner
        # angle of the rectangle, rotated by the orientation angle + 180 degrees to get its opposite
        theta = angle + math.degrees(math.atan2(aminor, amajor)) + 180.
        r = math.sqrt(amajor*amajor + aminor*aminor)/2.
        dx = r * math.cos(math.radians(theta))
        dy = r * math.sin(math.radians(theta))
        if ft in ['square', 'gray-square']:
            color = '#0f0' if ft == 'square' else '#999'
            r1 = patches.Rectangle((x + dx, y + dy), amajor, aminor, fill=True, color=color, angle=angle, alpha=alpha)
            r2 = patches.Rectangle((x + dx, y + dy), amajor, aminor, fill=False, color='#000', angle=angle)
            ax.add_patch(r1)
            ax.add_patch(r2)
        else:
            color = '#0f0' if ft == 'circle-square' else '#999'
            #print (f"MAJOR: {amajor} MINOR: {aminor}")
            r1 = patches.Rectangle((x + dx, y + dy), amajor, aminor, fill=True, color=color, angle=angle, alpha=alpha)
            r2 = patches.Rectangle((x + dx, y + dy), amajor, aminor, fill=False, color='k', angle=angle)
            c1 = patches.Circle((x, y), aminor/2., fill=True, color='#fff')
            c2 = patches.Circle((x, y), aminor/2., fill=False, color='#000')
            ax.add_patch(r1)
            ax.add_patch(r2)
            ax.add_patch(c1)
            ax.add_patch(c2)
    else: # marker
        test = ax.scatter(
            [x], [y],
            s=[50.], c=['#00f'], facecolors='none',
            marker = dso.object_type.marker_type,
            #fillstyle = 'none'
        )
    return ax


#####
#####
#####
#####
#####
def create_dso_finder_chart(dso, fov=8, mag_limit=9, 
        reversed=True,  # white on black or black on white
        save_file=False, # return a stream or a filename
        planets_dict = None,
        asteroid_list = None,
        utdt = None,
        axes=False,  # not generally used
        test=False   # not generally used
    ):
    times = [(time.perf_counter(), 'Start')]
    ts = load.timescale()
    t = ts.from_datetime(datetime.datetime.now(pytz.timezone('UTC')))
    eph = load('de421.bsp')
    earth = eph['earth']

    # Center the chart on the DSO
    center = earth.at(t).observe(dso.skyfield_object)
    projection = build_stereographic_projection(center)
    field_of_view_degrees = fov
    times.append((time.perf_counter(), 'Initialize Ephem'))

    # Start Plot!
    style = 'dark_background' if reversed else 'default'
    plt.style.use(style)
    fig, ax = plt.subplots(figsize=[8,8])
    angle = np.pi - field_of_view_degrees / 360.0 * np.pi
    limit = np.sin(angle) / (1.0 - np.cos(angle))
    times.append((time.perf_counter(), 'Start Plot'))

    ax, stars = map_hipparcos(ax, earth, t, mag_limit, projection, reversed=reversed)
    times.append((time.perf_counter(), 'Hipparcos'))
    ax = map_constellation_lines(ax, stars, reversed=reversed)
    times.append((time.perf_counter(), 'Constellation Lines'))
    ax = map_bright_stars(ax, earth, t, projection, points=False, annotations=True, reversed=reversed)
    times.append((time.perf_counter(), 'Bright Stars'))

    ##### other dsos
    other_dso_records = DSO.objects.exclude(pk = dso.pk).order_by('-major_axis_size')
    other_dsos = {'x': [], 'y': [], 'label': [], 'marker': []}
    for other in other_dso_records:
        x, y = projection(earth.at(t).observe(other.skyfield_object))
        if abs(x) > limit or abs(y) > limit:
            continue # not on the plot
        other_dsos['x'].append(x)
        other_dsos['y'].append(y)
        other_dsos['label'].append(other.shown_name)
        other_dsos['marker'].append(other.object_type.marker_type)
        ax = plot_dso(ax, x, y, other, alpha=0.7)
    xxx = np.array(other_dsos['x'])
    yyy = np.array(other_dsos['y'])
    for x, y, z in zip(xxx, yyy, other_dsos['label']):
        plt.annotate(
            z, (x, y), 
            textcoords='offset points',
            xytext=(5, 5),
            ha='left'
        )
    times.append((time.perf_counter(), 'Other DSOs'))

    ### Planets, Asteroids
    if planets_dict is not None and utdt is not None:
        ax, _ = map_planets(ax, None, planets_dict, earth, t, projection)
    times.append((time.perf_counter(), 'Planets'))

    if asteroid_list is not None and utdt is not None:
        ax, _ = map_asteroids(ax, None, asteroid_list, earth, t, projection, reversed=reversed)
    times.append((time.perf_counter(), 'Asteroids'))

    ##### this object
    object_x, object_y = projection(center)
    ax = plot_dso(ax, object_x, object_y, dso, reversed=reversed)
    this_dso_color = '#ffc' if reversed else 'k'
    plt.annotate(
        dso.shown_name, (object_x, object_y), 
        textcoords='offset points', xytext=(5,5), 
        ha='left', color=this_dso_color, weight='bold'
    )
    #ax = map_eyepiece(ax, diam=0.0038, reversed=reversed)
    ecolor = 'cyan' if reversed else "#999"
    eyepiece_fov = find_site_parameter('eyepiece-fov', default=60., param_type='float')
    circle1 = plt.Circle((0, 0), eyepiece_fov * 2.909e-4 / 2. / 2., color=ecolor, fill=False)
    ax.add_patch(circle1)
    times.append((time.perf_counter(), 'Done Mapping'))

    ### Finish up
    # scaling
    ax.set_xlim(-limit, limit)
    ax.set_ylim(-limit, limit)
    # axis labels
    if not axes:
        ax.xaxis.set_visible(False)
        ax.yaxis.set_visible(False)
    ax.set_aspect(1.0)

    # title
    title = "{}: {} in {}".format(dso.shown_name, dso.object_type, dso.constellation)
    if dso.nickname:
        title = "{} = ".format(dso.nickname) + title
    ax.set_title(title)
    times.append((time.perf_counter(), 'Set Limits/Add Title'))
    
    # legend
    #kw = dict(prop="sizes", num=6, fmt="{x:.2f}",
    #    func=lambda s: -1.*(np.sqrt(s)-0.5-limiting_magnitude) )
    #legend2 = ax.legend(*scatter.legend_elements(**kw), loc="upper left", title="Mag.")

    if save_file:
    # SAVE IT!
        if test:
            fn = 'test_{}.png'.format(dso.pk)
        else:
            fn = 'dso_chart_{}.png'.format(dso.shown_name.lower().replace(' ', '_'))

        try:
            fig.savefig('media/dso_charts/{}'.format(fn), bbox_inches='tight')
        except: # sometimes there's UTF-8 in the name
            fn = 'dso_chart_{}.png'.format(dso.pk)
            fig.savefig('media/dso_charts/{}'.format(fn), bbox_inches='tight')

        plt.cla()
        plt.close(fig)
        return fn
    
    # else return the file as a stream
        # Render and close
    # Convert to a PNG image
    pngImage = io.BytesIO()
    FigureCanvas(fig).print_png(pngImage)

    # Encode PNG to Base64 string
    pngImageB64String = 'data:image/png;base64,'
    pngImageB64String += base64.b64encode(pngImage.getvalue()).decode('utf8')

    # Close the plot
    plt.tight_layout()
    plt.cla()
    plt.close(fig)
    times.append((time.perf_counter(), 'Returning Image'))
    return pngImageB64String, times