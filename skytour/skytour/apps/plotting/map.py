import math
import matplotlib
import numpy as np
from matplotlib import pyplot as plt
from matplotlib.collections import LineCollection
from matplotlib.patches import Wedge, Ellipse
from skyfield.api import Star, load
from skyfield.data import hipparcos, stellarium
from ..dso.models import DSO
from ..solar_system.saturn import saturn_ring
from ..solar_system.vocabs import UNICODE
from ..stars.models import BrightStar

matplotlib.use('Agg')

def map_constellation_lines(ax, stars):
    url = ('https://raw.githubusercontent.com/Stellarium/stellarium/master'
        '/skycultures/western_SnT/constellationship.fab')
    with load.open(url) as f:
        constellations = stellarium.parse_constellations(f)
    edges = [edge for name, edges in constellations for edge in edges]
    edges_star1 = [star1 for star1, star2 in edges]
    edges_star2 = [star2 for star1, star2 in edges]

    # assemble constellation lines
    xy1 = stars[['x', 'y']].loc[edges_star1].values
    xy2 = stars[['x', 'y']].loc[edges_star2].values
    lines_xy = np.rollaxis(np.array([xy1, xy2]), 1)
    ##### constellation lines
    ax.add_collection(LineCollection(lines_xy, colors='#00f2'))
    return ax

def map_hipparcos(ax, earth, t, mag_limit, projection):
    with load.open(hipparcos.URL) as f:
        stars = hipparcos.load_dataframe(f)
    # Compute the X,Y coordinates of stars on the plot
    star_positions = earth.at(t).observe(Star.from_dataframe(stars))
    stars['x'], stars['y'] = projection(star_positions)
    bright_stars = (stars.magnitude <= mag_limit)
    magnitude = stars['magnitude'][bright_stars]
    marker_size = (0.5 + mag_limit - magnitude) **2.0
    ##### background stars
    scatter = ax.scatter(
        stars['x'][bright_stars], stars['y'][bright_stars], 
        s=marker_size, color='k'
    )
    return ax, stars

def map_bsc_labels(earth, t, projection):
    bsc_stars = BrightStar.objects.filter(name__isnull=False)
    bsc_list = {'x': [], 'y': [], 'label': []}
    for bsc in bsc_stars:
        x, y = projection(earth.at(t).observe(bsc.skyfield_object))
        bsc_list['x'].append(x)
        bsc_list['y'].append(y)
        bsc_list['label'].append(bsc.plot_label)
    return zip(bsc_list['x'], bsc_list['y'], bsc_list['label'])

def map_target(ax, ra, dec, projection, earth, t, symbol):
    object_x, object_y = projection(earth.at(t).observe(
        Star(ra_hours=ra.hours, dec_degrees=dec.degrees))
    )
    object_scatter = ax.scatter(
        [object_x], [object_y], 
        s=[90.], c=['#900'], 
        marker='+'
    )
        # Add an eyepiece circle, 32mm = 0.0038 radians
    eyepiece = plt.Circle((0, 0), 0.0038, color='b', fill=False)
    ax.add_patch(eyepiece)
    return ax

def map_eyepiece(ax):
    eyepiece = plt.Circle((0,0), 0.0038, color='b', fill=False)
    return ax

def map_moons(ax, planet, earth, t, projection, ang_size_radians, debug=False):
    moon_pos_list = {'x': [], 'y': [], 'label': [], 'd': [], 'o': []}

    dist_to_planet = planet['target'].distance().au
    max_sep = 0.
    try:
        for moon in planet['moons']:
            (moon_ra, moon_dec, moon_dist) = moon['target'].radec()
            x, y = projection(earth.at(t).observe(Star(ra_hours=moon_ra.hours, dec_degrees=moon_dec.degrees)))
            d = moon_dist.au
            sep = moon['target'].separation_from(planet['target']).radians
            if debug:
                print("{}: X: {:.3f} Y: {:.3f} SEP: {:.3f} ANG: {:.3f} ∆d: {:.3f}".format(
                    moon['name'], x*1e5, y*1e5, sep*1e5, 1e5*ang_size_radians/2., 1e5*(dist_to_planet - d))
                )
            dd = math.sqrt(x*x + y*y)
            if dd < ang_size_radians/2.:
            #if sep < ang_size_radians/2. and d > dist_to_planet:
                if debug:
                    print ("Removing: ", moon['name'])
                continue  # oops - I'm behind the planet
            if sep > max_sep:
                max_sep = sep

            # Continue    
            moon_pos_list['x'].append(x)
            moon_pos_list['y'].append(y)
            moon_pos_list['d'].append(d)
            l = moon['name'][0] # First initial
            if moon['name'] == 'Tethys':
                l = 'Te'
            elif moon['name'] == 'Titan':
                l = 'Ti'
            moon_pos_list['label'].append(l)
            if d < dist_to_planet:
                moon_pos_list['o'].append(-20)
            else:
                moon_pos_list['o'].append(10)

        moon_scatter = ax.scatter(moon_pos_list['x'], moon_pos_list['y'], color='b', marker='+')
    except:
        pass
    
    return ax, moon_pos_list, max_sep

def map_phased_planet(ax, planet, ang_size_radians):
    c1 = None
    e1 = None
    w1 = None
    w2 = None

    phase_angle = planet['observe']['plotting_phase_angle'] % 360. # in degrees
    major_axis = ang_size_radians  # radius of planet
    minor_axis = abs(math.cos(math.radians(planet['observe']['phase_angle'])) * ang_size_radians)
    #print("Phase: ", phase_angle, 'Major: ', major_axis, 'Minor: ', minor_axis)
    # Circumstances:
    #    phase:  0, 360:  minor  = 1.  New Moon        (left: black, right: black, half-ellipse: n/a really)
    if abs(phase_angle) < 2.: # New Moon
        c1 = plt.Circle((0,0), ang_size_radians/2., color='k') # black disk
    #    phase:   0- 90:  minor  > 0.  Waxing Crescent (left: black, right: white, half-ellipse: black)
    elif phase_angle < 178:
        w1 = Wedge((0,0), major_axis/2., -90., 90., fc='white', edgecolor='black')
        w2 = Wedge((0,0), major_axis/2., 90., 270., fc='black', edgecolor='black')
        if phase_angle <= 88. : # Waxing Crescent
            e1 = Ellipse((0,0), minor_axis, major_axis, fc='black', edgecolor='black')
    #                90:  minor  = 0.  First Quarter   (left: black, right: white, half-ellipse: n/a really)
    #            90-180:  minor  < 0.  Waxing Gibbous  (left: black, right: white, half-ellipse: white)
        elif phase_angle <= 178 and phase_angle >= 92.:
            e1 = Ellipse((0,0), minor_axis, major_axis, fc='black', edgecolor='black')
    #               180:  minor = -1.  Full Moon       (left: white, right: white, half-ellipse: n/a really)

    elif phase_angle < 182.: 
        c1 = plt.Circle((0,0), ang_size_radians/2., color='w') # white disk
    #           180-270:  minor  < 0.  Waning Gibbous  (left: white, right: black, half-ellipse: white)
    else:
        w1 = Wedge((0,0), major_axis/2., -90., 90., fc='black', edgecolor='black')
        w2 = Wedge((0,0), major_axis/2., 90., 270., fc='white', edgecolor='black')
        if phase_angle <= 268.: # waning gibbous
            e1 = Ellipse((0,0), minor_axis, major_axis, fc='black', edgecolor='black')
    #               270:  minor  = 0.  Last Quarter    (left: white, right: black, half-ellipse: n/a really)
    #           270-360:  minor  > 0.  Waning Crescent (left: white, right: black, half-ellipse: black)
        if phase_angle >= 272 and phase_angle < 358.:
            e1 = Ellipse((0,0), minor_axis, major_axis, fc='black', edgecolor='black') 

    # put in the wedges
    if w1: 
        ax.add_artist(w1)
    if w2:
        ax.add_artist(w2)
    # on top of that, the ellipse
    if e1:
        ax.add_patch(e1)
    # or the circle
    if c1:
        ax.add_patch(c1)
    # and for consistency, the red circle...
    circle2 = plt.Circle((0,0), ang_size_radians/2., color='r', fill=False)
    ax.add_patch(circle2)
    return ax

def map_whole_planet(ax, ang_size_radians):
    circle1 = plt.Circle((0,0), ang_size_radians/2., color='w')
    ax.add_patch(circle1)
    circle2 = plt.Circle((0,0), ang_size_radians/2., color='r', fill=False)
    ax.add_patch(circle2)
    return ax

def map_saturn_rings(ax, planet, t0):
    rings = saturn_ring(t0, planet['target'])
    a = math.radians(rings['major'] / 3600.)
    b = math.radians(rings['minor'] / 3600.)
    #print ("a: ", a, "b: ", b)
    re1 = Ellipse((0,0), a, b, fill=False)
    ax.add_patch(re1)
    re2 = Ellipse((0,0), a*.665, b*.665, fill=False)
    ax.add_patch(re2)
    return ax

def map_dsos(ax, earth, t, projection, dso=None):
    other_dso_records = DSO.objects.all()
    if dso:
        other_dso_records = other_dso_records.exclude(dso.pk)
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
    return ax, xxx, yyy, other_dsos

def map_planets(this_planet, planets, earth, t, projection):
    d = {'x': [], 'y': [], 'marker': []}
    planet_labels = []
    for k,v in planets.items():
        if k == this_planet:
            continue
        ra = v['coords']['ra']
        dec = v['coords']['dec']
        x, y = projection(earth.at(t).observe(Star(ra_hours=ra, dec_degrees=dec)))
        d['x'].append(x)
        d['y'].append(y)
        d['marker'].append(UNICODE[k])
    xxx = np.array(d['x'])
    yyy = np.array(d['y'])
    mmm = np.array(d['marker'])
    return xxx, yyy, mmm