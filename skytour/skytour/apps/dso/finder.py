import base64
import datetime, pytz
import io
import math
import numpy as np
import time

from matplotlib import pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib import patches

from skyfield.api import Star, load
from skyfield.projections import build_stereographic_projection

from ..plotting.map import *
from ..site_parameter.helpers import find_site_parameter
from .models import DSO
# Circular import issue...  Sigh.
from .const_utils import get_boundary_lines

### These are used to create a secondary axis on the plot.
def r2d(a): # a is a numpy.array
    return a * (180.*2) / math.pi
def d2r(a): # a us a numpy.array
    return a * math.pi / (180.*2)

def plot_other_dsos(
        ax, other_dso_records, projection, earth, t, 
        limit, times, reversed=False, in_field=False, fov_type='narrow'):
    
    other_dsos = {'x': [], 'y': [], 'label': [], 'marker': []}

    if fov_type == 'wide':
        #default_size = 1.0 if in_field else 5.0
        #min_size = 1.0 if in_field else 8.0
        default_size = 8.0
        min_size = 8.0
    else:
        default_size = 1.0
        min_size = 1.0

    #print(f"Other DSOs: {fov_type} plot DS: {default_size} MIN: {min_size}")

    max_size = 30
    for other in other_dso_records:
        x, y = projection(earth.at(t).observe(other.skyfield_object))
        if abs(x) > limit or abs(y) > limit:
            continue # not on the plot
        other_dsos['x'].append(x)
        other_dsos['y'].append(y)
        other_dsos['label'].append(other.label_on_chart)
        other_dsos['marker'].append(other.object_type.marker_type)
        ax = plot_dso(ax, x, y, other, alpha=0.6, 
            default_size=default_size, max_size=max_size, min_size=min_size,
            reversed=reversed
        )
    xxx = np.array(other_dsos['x'])
    yyy = np.array(other_dsos['y'])
    for x, y, z in zip(xxx, yyy, other_dsos['label']):
        if not in_field:
            plt.annotate(
                z, (x, y), 
                textcoords='offset points',
                xytext=(5, 5),
                ha='left',
                fontsize='x-small'
            )
        else:
            plt.annotate(
                z, (x, y),
                textcoords='offset points',
                xytext=(-5, -5),
                ha='right',
                fontsize='xx-small'
            )
    times.append((time.perf_counter(), 'Other DSOs'))
    return ax, times

def plot_dso(ax, x, y, dso, 
        color='r', 
        reversed=True, 
        alpha=.7, 
        min_size=1., 
        max_size=40.,
        default_size = None,
        debug = False
    ):
    """
    Put a DSO on the map with custom markers related to the object type.
    Scale the marker to the size and orientation of the object, if it's not
    too small (or large).
    """
    oangle = dso.orientation_angle or 0
    ft = dso.object_type.map_symbol_type

    default_size = default_size if default_size else min_size
    amajor = dso.major_axis_size if dso.major_axis_size is not None else default_size
    amajor = amajor if amajor != 0 else default_size
    aminor = amajor if dso.minor_axis_size is None or dso.minor_axis_size == 0 else dso.minor_axis_size
    if debug:
        print(f"DSO: {dso} {dso.major_axis_size} x {dso.minor_axis_size} D: {default_size} 0: {min_size}")

    ratio = aminor / amajor
    if amajor < min_size:
        if debug:
            print("\t TOO SMALL")
        amajor = min_size
        aminor = min_size * ratio
    if amajor > max_size:
        if debug:
            print("\t TOO BIG")
        amajor = max_size
        aminor = max_size * ratio
    if debug:
        print(f"\t finally {amajor} x {aminor}")

    # Deal with size
    amajor *= 2.909e-4
    aminor *= 2.909e-4
    # 6. Also, rotate by the position angle where appropriate.
    angle = oangle
    umajor = amajor / 2.
    uminor = aminor / 2.
    
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

    if ft == 'ellipse': # galaxies
        color = '#99f' if 'barred' in dso.object_type.slug.lower() else '#f00'
        color = '#c6f' if 'ellip' in dso.object_type.slug.lower() else color
        color = '#c6f' if 'lenti' in dso.object_type.slug.lower() else color
        color = '#09f' if 'dwarf' in dso.object_type.slug.lower() else color
        color = '#c69' if 'irreg' in dso.object_type.slug.lower() else color
        e1 = patches.Ellipse((x, y), uminor, umajor, angle=angle, fill=True, color=color, alpha=alpha)
        e2 = patches.Ellipse((x, y), uminor, umajor, angle=angle, fill=False, color='#999')
        ax.add_patch(e1)
        ax.add_patch(e2)

    elif ft in ['open-circle', 'gray-circle', 'circle-plus']: # clusters
        color = '#999' if ft == 'gray-circle' else '#ff0'
        radius = umajor / 2.  # Why?  I don't know but the circles are always to large
        c1 = patches.Circle((x, y), radius, fill=True, color=color, alpha=alpha)
        r_color = '#fff' if reversed else '#000'
        c2 = patches.Circle((x, y), radius, fill=False, color=r_color)
        if ft == 'circle-plus':
            cp_color = '#ccc' if reversed else '#000'
            #ax.vlines(x, y-amajor/2, y+amajor/2, color=cp_color)
            #ax.hlines(y, x-amajor/2, x+amajor/2, color=cp_color)
            ax.vlines(x, y-radius, y+radius, color=cp_color)
            ax.hlines(y, x-radius, x+radius, color=cp_color)
        ax.add_patch(c1)
        ax.add_patch(c2)

    elif ft in ['square', 'gray-square', 'circle-square', 'circle-gray-square', 'two-squares']: # UGH - the center point is the lower-left corner
        # angle of the rectangle, rotated by the orientation angle + 180 degrees to get its opposite
        theta = angle + math.degrees(math.atan2(aminor, amajor)) + 180.
        r = math.sqrt(umajor*umajor + uminor*uminor)/2.
        dx = r * math.cos(math.radians(theta))
        dy = r * math.sin(math.radians(theta))
        if ft in ['square', 'gray-square']:
            color = '#6f6' if ft == 'square' else '#999'
            r1 = patches.Rectangle((x + dx, y + dy), umajor, uminor, fill=True, color=color, angle=angle, alpha=alpha)
            r2 = patches.Rectangle((x + dx, y + dy), umajor, uminor, fill=False, color='#000', angle=angle)
            ax.add_patch(r1)
            ax.add_patch(r2)
        elif ft == 'two-squares':
            color = '#c0c'
            r1 = patches.Rectangle((x + dx, y + dy ), umajor, uminor, fill=True, color=color, angle=angle, alpha=alpha/2.)
            r2 = patches.Rectangle((x + dx, y + dy ), umajor, uminor, fill=False, color=color, angle=angle)
            ax.add_patch(r1)
        else:
            color = '#6f6' if ft == 'circle-square' else '#999'
            r1 = patches.Rectangle((x + dx, y + dy), umajor, uminor, fill=True, color=color, angle=angle, alpha=alpha)
            r2 = patches.Rectangle((x + dx, y + dy), umajor, uminor, fill=False, color='k', angle=angle)
            c1 = patches.Circle((x, y), uminor, fill=True, color='#fff', alpha=alpha*.5)
            c2 = patches.Circle((x, y), uminor, fill=False, color='#000')
            ax.add_patch(r1)
            ax.add_patch(r2)
            ax.add_patch(c1)
            ax.add_patch(c2)

    elif ft in ('two-circles'):
        ccolor = '#3fc' if reversed else '#3c9'
        radius = umajor / 2.
        c1 = patches.Circle((x, y), radius, fill=False, color=ccolor)
        c2 = patches.Circle((x, y), 0.75 * radius, fill=False, color=ccolor)
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

def create_dso_finder_chart(
        dso, 
        fov=8., 
        mag_limit=9., 
        reversed=True,  # white on black or black on white
        save_file=False, # return a stream or a filename
        planets_dict = None,
        asteroid_list = None,
        comet_list = None,
        utdt = None,
        show_other_dsos = True,
        show_in_field_dsos = False,
        now = False,
        chart_type = 'wide',
        axes = False,  # not generally used
        test = False,   # not generally used
        path = 'media/dso_charts/',
        gear_list = ['eyepiece', 'equinox2', 'seestar50', 'seestar30'],
        include_mosaic = False,
        ts = None, eph = None, t = None, earth = None
    ):
    """
    Create a finder chart for a DSO for a given date.
    Overlay planets and asteroids to this chart.
    """
    path = 'media/dso_charts/' if path is None else path
    times = [(time.perf_counter(), 'Start')]
    if ts is None or t is None or eph is None or earth is None:
        print("Getting DT metadata!")
    ts = load.timescale() if ts is None else ts
    if t is None:
        t = ts.from_datetime(datetime.datetime.now(pytz.timezone('UTC'))) 
    if eph is None:
        eph = load('de421.bsp') 
    earth = eph['earth'] if earth is None else earth

    # Center the chart on the DSO
    center = earth.at(t).observe(dso.skyfield_object)
    projection = build_stereographic_projection(center)
    field_of_view_degrees = fov
    times.append((time.perf_counter(), 'Initialize Ephem'))

    # Start Plot!
    style = 'dark_background' if reversed else 'default'
    plt.style.use(style)
    fig, ax = plt.subplots(figsize=[8,8])
    angle = np.pi - field_of_view_degrees  / 360.0 * np.pi
    limit = np.sin(angle) / (1.0 - np.cos(angle))
    times.append((time.perf_counter(), 'Start Plot'))

    ax = map_equ(ax, earth, t, projection, 'equ', reversed=reversed)
    ax = map_equ(ax, earth, t, projection, 'ecl', reversed=reversed)
    ax = map_equ(ax, earth, t, projection, 'gal', reversed=reversed)
    ax, stars = map_hipparcos(ax, earth, t, mag_limit, projection, reversed=reversed)
    times.append((time.perf_counter(), 'Hipparcos'))
    ax = map_constellation_lines(ax, stars, reversed=reversed)
    times.append((time.perf_counter(), 'Constellation Lines'))
    # circular import... ugh
    lines, _ = get_boundary_lines(dso.constellation.abbreviation, 'constellation')
    ax = new_map_constellation_boundaries(ax, lines, earth, t, projection, reversed=False)

    ax = map_bright_stars(ax, earth, t, projection, points=False, annotations=True, reversed=reversed)
    times.append((time.perf_counter(), 'Bright Stars'))

    ##### this object
    object_x, object_y = projection(center)
    if chart_type == 'wide':
        ax = plot_dso(ax, object_x, object_y, dso, reversed=reversed, min_size=8)
    else:
        ax = plot_dso(ax, object_x, object_y, dso, reversed=reversed)

    this_dso_color = '#ffc' if reversed else 'k'
    my_label = dso.label_on_chart if chart_type == 'wide' else dso.shown_name
    plt.annotate(
        my_label, (object_x, object_y), 
        textcoords='offset points', xytext=(5,5), 
        ha='left', color=this_dso_color, weight='bold'
    )
    ##### other dsos
    if show_other_dsos:
        # TODO: This is inefficient: should use the dso.nearby_dsos property to get a list
        # unless the FOV for "wide" is so wide that that won't work?
        other_dso_records = DSO.objects.exclude(pk = dso.pk).order_by('-major_axis_size')
        ax, times = plot_other_dsos(ax, other_dso_records, projection, earth, t, limit, times, in_field=False, reversed=reversed, fov_type=chart_type)

    if show_in_field_dsos:
        if dso.dsoinfield_set.count() > 0:
            # My infield DSOs
            in_field_dsos = dso.dsoinfield_set.all()
            ax, times = plot_other_dsos(ax, in_field_dsos, projection, earth, t, limit, times, in_field=True, reversed=reversed)
        # Neighbor infield DSOs
        nearby_dsos = dso.nearby_dsos
        for ndso in nearby_dsos:
            if ndso is not None and ndso.dsoinfield_set.count() > 0:
                nin_field_dsos = ndso.dsoinfield_set.all()
                ax, times = plot_other_dsos(ax, nin_field_dsos, projection, earth, t, limit, times, in_field=True, reversed=reversed)

    ### Planets, Asteroids
    if planets_dict is not None and utdt is not None and now:
        ax, _ = map_planets(ax, None, planets_dict, earth, t, projection)
        times.append((time.perf_counter(), 'Planets'))

    if asteroid_list is not None and utdt is not None and now:
        ax, _ = map_asteroids(ax, None, asteroid_list, earth, t, projection, reversed=reversed)
        times.append((time.perf_counter(), 'Asteroids'))

    if comet_list is not None and utdt is not None and now:
        ax, _ = map_comets(ax, comet_list, earth, t, projection, reversed=reversed)


    #ax = map_eyepiece(ax, diam=0.0038, reversed=reversed)
    if 'eyepiece' in gear_list:
        ecolor = 'cyan' if reversed else "#999"
        eyepiece_fov = find_site_parameter('eyepiece-fov', default=60., param_type='float')
        circle1 = plt.Circle((0, 0), eyepiece_fov * 2.909e-4 / 2. / 2., color=ecolor, fill=False)
        ax.add_patch(circle1)

    # eQuinox2 rectangle
    if 'equinox2' in gear_list:
        width = 47. * 2.909e-4 / 2.
        height = 34. * 2.909e-4 / 2.
        x0 = -width / 2.
        y0 = -height / 2.
        rect1 = plt.Rectangle((x0, y0), width, height, color='#f00', fill=False)
        ax.add_patch(rect1)

    # Seestar S50 rectangle
    mosaic_linestyle = (0, (3, 2, 1, 2, 1, 2)) # (5, (10,3))
    if 'seestar50' in gear_list:
        s50color = '#fa0' if reversed else '#c80'
        h1 = 1.29 * 60 * 2.909e-4 / 2.
        w1 = 0.73 * 60 * 2.909e-4 / 2.
        x1 = -w1 / 2.
        y1 = -h1 / 2.
        rect2 = plt.Rectangle((x1, y1), w1, h1, 
            color=s50color, fill=False
        )
        ax.add_patch(rect2)

        # Include S50 mosaic
        if include_mosaic:
            h1m = 2 * h1
            w1m = 2 * w1
            x1m = -w1m / 2.
            y1m = -h1m / 2.
            rect2m = plt.Rectangle((x1m, y1m), w1m, h1m, 
                color=s50color, fill=False, linestyle=mosaic_linestyle
            )
            ax.add_patch(rect2m)

    # Seestar S30 rectangle
    if 'seestar30' in gear_list:
        s30color = '#3cf' if reversed else '#0ae'
        h2 = 2.17 * 60 * 2.909e-4 / 2.
        w2 = 1.22 * 60 * 2.909e-4 / 2.
        x2 = -w2 / 2.
        y2 = -h2 / 2.
        rect3 = plt.Rectangle((x2, y2), w2, h2, 
            color=s30color, fill=False
        )
        ax.add_patch(rect3)

        # Include S30 mosaic
        if include_mosaic:
            h2m = 2 * h2
            w2m = 2 * w2
            x2m = -w2m / 2.
            y2m = -h2m / 2.
            rect3m = plt.Rectangle((x2m, y2m), w2m, h2m, 
                color=s30color, fill=False, linestyle=mosaic_linestyle
            )
            ax.add_patch(rect3m)

    times.append((time.perf_counter(), 'Done Mapping'))

    ### Finish up
    # scaling
    ax.set_xlim(-limit, limit)
    ax.set_ylim(-limit, limit)
    # axis labels
    if not axes:
        ax.xaxis.set_visible(False)
        ax.yaxis.set_visible(False)
    secax = ax.secondary_xaxis('bottom', functions=(r2d, d2r))
    secax.set_xlabel('Degrees')
    secay = ax.secondary_yaxis('left', functions=(r2d, d2r))
    ax.set_aspect(1.0)

    # title
    title = "{}: {} in {}".format(dso.label_on_chart, dso.object_type, dso.constellation)
    if dso.nickname:
        title = "{} = ".format(dso.nickname) + title
    ax.set_title(title)
    times.append((time.perf_counter(), 'Set Limits/Add Title'))
    
    # legend
    #kw = dict(prop="sizes", num=6, fmt="{x:.2f}",
    #    func=lambda s: -1.*(np.sqrt(s)-0.5-limiting_magnitude) )
    #legend2 = ax.legend(*scatter.legend_elements(**kw), loc="upper left", title="Mag.")

    if save_file:
        if test:
            fn = 'test_{}.png'.format(dso.pk)
        else:
            fn = 'dso_chart_{}.png'.format(dso.shown_name.lower().replace(' ', '_'))

        if test:
            print(f"Saving to {path}{fn}")
        try:
            fig.savefig('{}{}'.format(path, fn), bbox_inches='tight')
        except: # sometimes there's UTF-8 in the name
            fn = 'dso_chart_{}.png'.format(dso.pk)
            fig.savefig('{}{}'.format(path, fn), bbox_inches='tight')

        plt.cla()
        plt.close(fig)
        return fn

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

def plot_dso_list(center_ra, center_dec, dso_list, fov=20, mag_limit=9, 
        reversed=True,  # white on black or black on white
        title='DSO List',
        star_mag_limit = 11,
        symbol_size=40,
        label_size='xx-small',
    ):
    ts = load.timescale()
    t = ts.from_datetime(datetime.datetime.now(pytz.timezone('UTC')))
    eph = load('de421.bsp')
    earth = eph['earth']

    # Center the chart on the DSO
    center = earth.at(t).observe(Star(ra_hours=center_ra, dec_degrees=center_dec))
    projection = build_stereographic_projection(center)

    # Start up a Matplotlib plot
    style = 'dark_background' if reversed else 'default'
    plt.style.use(style)
    fig, ax = plt.subplots(figsize=[8,8])

    # Stars
    ax, stars = map_hipparcos(ax, earth, t, star_mag_limit, projection, mag_offset=0.1, reversed=reversed)
    ax = map_constellation_lines(ax, stars, reversed=reversed)
    ax = map_bright_stars(
        ax, earth, t, projection, mag_limit=3.0, points=False, annotations=True, reversed=reversed
    )
    ax, _ = map_dsos(ax, earth, t, projection, 
        center = (center_ra, center_dec),
        dso_list = dso_list,
        label_size=label_size,
        symbol_size=symbol_size,
        reversed=reversed,
        product = 'finder',
        ignore_setting = True
    )
    angle = np.pi - fov / 360. * np.pi
    limit = np.sin(angle) / (1.0 - np.cos(angle))
    ax.set_xlim(-limit, limit)
    ax.set_ylim(-limit, limit)
    ax.xaxis.set_visible(False)
    ax.yaxis.set_visible(False)
    secax = ax.secondary_xaxis('bottom', functions=(r2d, d2r))
    secax.set_xlabel('Degrees')
    secay = ax.secondary_yaxis('left', functions=(r2d, d2r))
    plt.tight_layout(pad=2.0)

    ax.set_title(title)
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

    return pngImageB64String