

import numpy as np
import datetime
import pytz
from django.core.management.base import BaseCommand
from matplotlib import pyplot as plt
from matplotlib.collections import LineCollection
from skyfield.api import Star, load
from skyfield.data import hipparcos, mpc, stellarium
from skyfield.projections import build_stereographic_projection
from skytour.apps.stars.models import BrightStar
from skytour.apps.dso.models import DSO

def create_dso_finder_chart(dso, fov=8, mag0=9, axes=False):
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

    ##### constellation lines
    ax.add_collection(LineCollection(lines_xy, colors='#00f2'))

    ##### background stars
    scatter = ax.scatter(
        stars['x'][bright_stars], stars['y'][bright_stars], 
        s=marker_size, color='k'
    )

    ##### other dsos
    other_dso_records = DSO.objects.exclude(pk = dso.pk)
    other_dsos = {'x': [], 'y': [], 'label': [], 'marker': []}
    for other in other_dso_records:
        x, y = projection(earth.at(t).observe(other.skyfield_object))
        other_dsos['x'].append(x)
        other_dsos['y'].append(y)
        other_dsos['label'].append(other.shown_name)
        other_dsos['marker'].append(other.object_type.marker_type)
    xxx = np.array(other_dsos['x'])
    yyy = np.array(other_dsos['y'])
    mmm = np.array(other_dsos['marker'])
    # This is tricky for the different markers:
    unique_markers = set(mmm)
    for um in unique_markers:
        mask = mmm == um
        ax.scatter(
            xxx[mask], yyy[mask],
            s=90., edgecolor='g', facecolors='none',
            marker=um
        )
    for x, y, z in zip(xxx, yyy, other_dsos['label']):
        plt.annotate(
            z, (x, y), 
            textcoords='offset points',
            xytext=(5, 5),
            ha='left'
        )

    ##### this object
    object_x, object_y = projection(center)
    object_scatter = ax.scatter(
        [object_x], [object_y], 
        s=[90.], c=['#f00'], facecolors='none',
        marker=dso.object_type.marker_type
    )
    plt.annotate(
        dso.shown_name, (object_x, object_y), 
        textcoords='offset points', xytext=(5,5), 
        ha='left', color='#f00'
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

    # Add an eyepiece circle, 32mm = 0.0038 radians
    circle1 = plt.Circle((0, 0), 0.0036, color='b', fill=False)
    ax.add_patch(circle1)

    ### Finish up

    # scaling
    angle = np.pi - field_of_view_degrees / 360.0 * np.pi
    limit = np.sin(angle) / (1.0 - np.cos(angle))
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
    
    def handle(self, *args, **kwargs):
        dsos = DSO.objects.all()
        for dso in dsos:
            if dso.dso_finder_chart:
                continue
            print("Creating Finder Chart for {}: {}".format(dso.pk, dso.shown_name))
            fn = create_dso_finder_chart(dso)
            dso.dso_finder_chart = 'dso_charts/{}'.format(fn)
            #print ("\tFN: ", fn)
            dso.save()