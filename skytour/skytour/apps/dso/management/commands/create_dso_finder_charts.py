

import math
import numpy as np
import datetime
import pytz
from django.core.management.base import BaseCommand
from matplotlib import pyplot as plt
from matplotlib.collections import LineCollection
from matplotlib import patches
from skyfield.api import Star, load
from skyfield.data import hipparcos, mpc, stellarium
from skyfield.projections import build_stereographic_projection
from skytour.apps.stars.models import BrightStar
from skytour.apps.dso.models import DSO

def plot_dso(ax, x, y, dso, color='r', size_limit=0.0005, alpha=1):
    oangle = dso.orientation_angle or 0
    ft = dso.object_type.map_symbol_type
    aminor = dso.minor_axis_size * 2.909e-4 # total width
    amajor = dso.major_axis_size * 2.909e-4 # total length
    if aminor == 0 and amajor != 0:
        aminor = amajor
    angle = 90 - oangle

    if amajor < size_limit or aminor < size_limit: # if it's too small put the marker there instead
        ft = 'marker'

    #('marker', 'Marker'),                               # default - star like things, or unknown
    #('ellipse', 'Ellipse'),                             # galaxies - maybe not irregular
    #('open-circle', 'Open Circle'),                     # open clusters, associations
    #('gray-circle', 'Gray Circle'),                     # globular clusters
    #('circle-square', 'Circle in Square'),              # planetary nebulae
    #('square', 'Open Square'),                          # Emission Nebulae
    #('gray-square', 'Gray Square'),                     # Dark Nebulae
    #('circle-gray-square', 'Circle in Gray Square')     # cluster w/ nebulosity
    print (f'{ft}: X: {x:.3f} Y: {y:.3f}    A: {amajor:.4f}  B: {aminor:.4f}  O: {angle:3d} T: {alpha:.1f}')
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

def create_dso_finder_chart(dso, fov=8, mag0=9, axes=False, test=False):
    ts = load.timescale()
    t = ts.from_datetime(datetime.datetime.now(pytz.timezone('UTC')))
    eph = load('de421.bsp')
    earth = eph['earth']

    # Hipparcos
    with load.open(hipparcos.URL) as f:
        stars = hipparcos.load_dataframe(f)
    
    # Constellations
    url = ('https://raw.githubusercontent.com/Stellarium/stellarium/master'
    '/skycultures/western_SnT/constellationship.fab')
    with load.open(url) as f:
        constellations = stellarium.parse_constellations(f)
    edges = [edge for name, edges in constellations for edge in edges]
    edges_star1 = [star1 for star1, star2 in edges]
    edges_star2 = [star2 for star1, star2 in edges]

    # Center the chart on the DSO
    center = earth.at(t).observe(dso.skyfield_object)
    projection = build_stereographic_projection(center)
    field_of_view_degrees = fov
    limiting_magnitude = mag0

    # Compute the X,Y coordinates of stars on the plot
    star_positions = earth.at(t).observe(Star.from_dataframe(stars))
    stars['x'], stars['y'] = projection(star_positions)
    bright_stars = (stars.magnitude <= limiting_magnitude)
    magnitude = stars['magnitude'][bright_stars]
    marker_size = (0.5 + limiting_magnitude - magnitude) **2.0

    # assemble constellation lines
    xy1 = stars[['x', 'y']].loc[edges_star1].values
    xy2 = stars[['x', 'y']].loc[edges_star2].values
    lines_xy = np.rollaxis(np.array([xy1, xy2]), 1)

    # Start Plot!
    fig, ax = plt.subplots(figsize=[8,8])
    angle = np.pi - field_of_view_degrees / 360.0 * np.pi
    limit = np.sin(angle) / (1.0 - np.cos(angle))

    ##### this object (on the bottom)
    object_x, object_y = projection(center)
    ax = plot_dso(ax, object_x, object_y, dso)
    #object_scatter = ax.scatter(
    #    [object_x], [object_y], 
    #    s=[90.], c=['#f00'], facecolors='none',
    #    marker=dso.object_type.marker_type
    #)    
    plt.annotate(
        dso.shown_name, (object_x, object_y), 
        textcoords='offset points', xytext=(5,5), 
        ha='left', color='k', weight='bold'
    )

    ##### constellation lines
    ax.add_collection(LineCollection(lines_xy, colors='#00f2'))

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
    mmm = np.array(other_dsos['marker'])
    # This is tricky for the different markers:
    """
    unique_markers = set(mmm)
    for um in unique_markers:
        mask = mmm == um
        ax.scatter(
            xxx[mask], yyy[mask],
            s=90., edgecolor='g', facecolors='none',
            marker=um
        )
    """
    for x, y, z in zip(xxx, yyy, other_dsos['label']):
        plt.annotate(
            z, (x, y), 
            textcoords='offset points',
            xytext=(5, 5),
            ha='left'
        )


    ##### background stars
    scatter = ax.scatter(
        stars['x'][bright_stars], stars['y'][bright_stars], 
        s=marker_size, color='k'
    )

    ##### BSC
    bsc_stars = BrightStar.objects.filter(name__isnull=False)
    bsc_list = {'x': [], 'y': [], 'label': []}
    for bsc in bsc_stars:
        x, y = projection(earth.at(t).observe(bsc.skyfield_object))
        bsc_list['x'].append(x)
        bsc_list['y'].append(y)
        bsc_list['label'].append(bsc.plot_label)
    for x, y, z in zip(bsc_list['x'], bsc_list['y'], bsc_list['label']):
        plt.annotate(
            z, (x, y), 
            textcoords='offset points',
            xytext=(-8, -8),
            ha='right'
        )

    # Add an eyepiece circle, 32mm = 0.0036 radians
    circle1 = plt.Circle((0, 0), 0.0036, color='#999', fill=False)
    ax.add_patch(circle1)

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
    
    # legend
    kw = dict(prop="sizes", num=6, fmt="{x:.2f}",
        func=lambda s: -1.*(np.sqrt(s)-0.5-limiting_magnitude) )
    legend2 = ax.legend(*scatter.legend_elements(**kw), loc="upper left", title="Mag.")

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

class Command(BaseCommand):
    help = 'Create DSO finder charts'

    def add_arguments(self, parser):
        parser.add_argument('--dso_list', dest='dso_list', nargs='+', type=int)
        parser.add_argument('--all', dest='all', action='store_true')
        parser.add_argument('--test', action='store_true')
    
    def handle(self, *args, **options):
        """
        Three ways this can run:
            - Create all new maps for all DSOs (all = True)
            - Create/Update maps for a subset of DSOs (dso_list=[ list of PKs ])
            - Create maps for DSOs that don't already have one (all=False, no dso_list)
        """
        dso_list = None
        all = False
        just_new = False

        if options['all']:
            all = options['all']
            print ("ALL is true")
        elif options['dso_list']:
            dso_list = options['dso_list']
            print ("GOT DSOs: ", dso_list)
        else:
            just_new = True
            print ("Running new DSOs")

        if dso_list:
            dsos = DSO.objects.filter(pk__in=dso_list)
        else:
            dsos = DSO.objects.all()

        for dso in dsos:
            if just_new and dso.dso_finder_chart:
                continue
            
            # Otherwise operate!
            print("Creating/Updating Finder Chart for {}: {}".format(dso.pk, dso.shown_name))

            fn = create_dso_finder_chart(dso, test=options['test'])
            if not options['test']:
                dso.dso_finder_chart = 'dso_charts/{}'.format(fn)
                #print ("\tFN: ", fn)
                dso.save()