import math
import matplotlib
import numpy as np
from matplotlib import pyplot as plt
from matplotlib.collections import LineCollection
from matplotlib.patches import Wedge, Ellipse
from skyfield.api import Star, load
from skyfield.data import hipparcos, stellarium
from ..dso.models import DSO
from ..site_parameter.helpers import find_site_parameter
from ..solar_system.comets import get_comet
from ..solar_system.meteors import get_meteor_showers
from ..solar_system.models import Comet
from ..solar_system.saturn import saturn_ring
from ..solar_system.vocabs import UNICODE
from ..stars.models import BrightStar
from ..utils.astro import get_altitude

matplotlib.use('Agg') # This gets around some of Matplotlib's oddities

"""
Each of the methods create a piece of a map.
Each takes the matplotlib.Axes object instance (ax), does some operation,
and returns it "back" to whatever is assembling the plot.
"""

def map_constellation_lines(ax, stars):
    """
    This requires that the map_hipparcos() method run first, since it
    gets the list of stars FROM the return of that method.
    """
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
    """
    Put down sized points for stars.
    While this DOES pre-filter by mag_limit it does NOT filter
    by proximity to the center of the map and its scale!

    TODO: generate some timing tests.
    """
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

def map_bright_stars(ax, earth, t, projection, mag_limit=None, points=True, annotations=True):
    """
    Use the Bright Star Catalog to annotate bright stars (since that information is
    not in the Hipparcos data file).

    This COULD be used to also make star plots, I suppose, but I just use 
    map_hipparcos with a mag_limit close to naked-eye limit...
    """
    bsc_stars = BrightStar.objects.filter(name__isnull=False)
    if mag_limit:
        bsc_stars = bsc_stars.exclude(magnitude__gte=mag_limit)
    bsc_list = {'x': [], 'y': [], 'label': [], 'size': []}
    for bsc in bsc_stars:
        x, y = projection(earth.at(t).observe(bsc.skyfield_object))
        bsc_list['x'].append(x)
        bsc_list['y'].append(y)
        bsc_list['label'].append(bsc.plot_label)
        if mag_limit is None:
            mag_limit = 7.
        bsc_list['size'].append((0.5 + mag_limit - bsc.magnitude) **2)

    if points:
        scatter = ax.scatter(
            bsc_list['x'], bsc_list['y'],
            s=bsc_list['size'], color='k'
        )
    if annotations:
        for x, y, z in zip(bsc_list['x'], bsc_list['y'], bsc_list['label']):
            ax.annotate(
                z, xy=(x, y), 
                textcoords='offset points',
                xytext=(-5, -5),
                horizontalalignment='right',
                annotation_clip = True
            )
    return ax

def map_target(ax, ra, dec, projection, earth, t, symbol):
    """
    This just puts a symbol on the map.
    For finding charts, I use this.
    """
    object_x, object_y = projection(earth.at(t).observe(
        Star(ra_hours=ra.hours, dec_degrees=dec.degrees))
    )
    object_scatter = ax.scatter(
        [object_x], [object_y], 
        s=[90.], c=['#900'], 
        marker='+'
    )
    # Add an eyepiece circle, 32mm = 0.00714 units
    fov = find_site_parameter('eyepiece-fov', default=60., param_type='float')
    eyepiece = plt.Circle((0, 0), fov * 2.909e-4 / 2., color='b', fill=False)
    ax.add_patch(eyepiece)
    return ax

def map_eyepiece(ax, diam=None):
    """
    the default is 1° FOV.
    """
    fov = find_site_parameter('eyepiece-fov', default=60., param_type='float')
    radius = diam/2 if diam is not None else fov * 2.909e-4 / 2.
    eyepiece = plt.Circle((0,0), radius, color='b', fill=False)
    return ax

def map_moons(ax, planet, earth, t, projection, ang_size_radians, debug=False):
    """
    Given the RA/Dec for the moons in a system, plot them against a rendering of
    the planet's angular diameter (and in the case of Saturn the projection of
    the rings).

    This just does the moons.   It puts a plus at the position, and an annotation
    for which moon it is (usually from the first letter, but Te/Ti in the case of
    Saturn's Tethys and Titan).

    NOTE:  the position of the annotation conveys information!
        - If it's above the moon, the moon is "behind" the planet in its orbit.
        - If it's below the moon, the moon is "in front of" the planet in its orbit.
    Moons that are eclipsed by the planet (behind and with a distance < the angular
    semi-diameter of the planet) are not shown.
    """
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
            if d < dist_to_planet:  # I'm in front of the planet
                moon_pos_list['o'].append(-20)
            else: # I'm behind the planet!
                moon_pos_list['o'].append(10)

        moon_scatter = ax.scatter(moon_pos_list['x'], moon_pos_list['y'], color='b', marker='+')
    except:
        pass # bail -- oops.
    return ax, moon_pos_list, max_sep

def map_phased_planet(ax, planet, ang_size_radians):
    """
    This is for planets with a disk that shows phases.
    Oh - yeah - and the Moon.  :-)

    How this works:  I'm cheating a little.  :-)   Given SOME measure of where the limb
    is on the disk of the object (or where it is in its orbit), generate:
        - two semi-hemispheres (the left and right sides):
            - if you look at a FQ or LQ moon, you have a dark side and a bright side.
        - a central ellipse that is the projection of the limb angle on the disk.
    SO - what this means is that you can get away with figuring out "is each piece
    bright or dark" for "left", "right" and the "ellipse" --- using the Moon as 
    an example:
        - New moon: left = right = dark and there's no ellipse
        - Wax. Cr.: left is dark, right is light, ellipse is dark
        - FQ: left is dark, right is bright, no ellipse
        - Wax. Gi.: left is dark, right is bright, ellipse is bright
        - Full (you can see where this is going)
        - Wan. Gi.: left is bright, right is (now) dark, and ellipse is bright.
        - ... and so on.

    Inferior planets don't have the same definitions.  If we define the phase_in_the_orbit
    to be 0 at superior conjunction, 180 at inferior conjunction, 90 at greatest W elongation
    and 270 at E, you can generate a SIMILAR logic, but mostly the ellipse color is 
    reversed from the Moon.

    At least that's what several hours of trial and error finally got me to think. :-)
    """
    ### OK SO, the phase angle's meaning is COMPLETELY DIFFERENT from the Moon
    # and inferior planets, and that makes sense IF you think about it, but it's
    # a PITA to get around without a lot of mental angle flipping, etc.
    # Basically, what ends up happening is that if you use what works for the Moon,

    cir1 = None
    ell1 = None
    wed1 = None
    wed2 = None

    ###
    ### For inferior planets the Ellipse is the reverse color than for the Moon.
    ###
    phase_angle = planet['observe']['plotting_phase_angle'] % 360. # in degrees
    major_axis = ang_size_radians  # radius of planet
    minor_axis = abs(math.cos(math.radians(planet['observe']['phase_angle'])) * ang_size_radians)

    is_moon = planet['name'] == 'Moon'
    if is_moon:
        c0 = 'black'
        c1 = 'white'
    else:
        c1 = 'black'
        c0 = 'white'

    #print("Phase: ", phase_angle, 'Major: ', major_axis, 'Minor: ', minor_axis)
    # Circumstances:
    #    phase:  0, 360:  minor  = 1.  New Moon        (left: black, right: black, half-ellipse: n/a really)
    if abs(phase_angle) < 2.: # New Moon
        cir1 = plt.Circle((0,0), ang_size_radians/2., color='k') # black disk
    #    phase:   0- 90:  minor  > 0.  Waxing Crescent (left: black, right: white, half-ellipse: black)
    elif phase_angle < 178:
        wed1 = Wedge((0,0), major_axis/2., -90., 90., fc='white', edgecolor='black')
        wed2 = Wedge((0,0), major_axis/2., 90., 270., fc='black', edgecolor='black')
        if phase_angle <= 88. : # Waxing Crescent
            ell1 = Ellipse((0,0), minor_axis, major_axis, fc=c0, edgecolor=c0)
    #                90:  minor  = 0.  First Quarter   (left: black, right: white, half-ellipse: n/a really)
    #            90-180:  minor  < 0.  Waxing Gibbous  (left: black, right: white, half-ellipse: white)
        elif phase_angle <= 178 and phase_angle >= 92.:
            # AH - but this is different for the Moon and inferior planets!
            ell1 = Ellipse((0,0), minor_axis, major_axis, fc=c1, edgecolor=c1)
    #               180:  minor = -1.  Full Moon       (left: white, right: white, half-ellipse: n/a really)

    elif phase_angle < 182.: 
        cir1 = plt.Circle((0,0), ang_size_radians/2., color='w') # white disk
    #           180-270:  minor  < 0.  Waning Gibbous  (left: white, right: black, half-ellipse: white)
    else: # angle between 182 and 358
        wed1 = Wedge((0,0), major_axis/2., -90., 90., fc='black', edgecolor='black')
        wed2 = Wedge((0,0), major_axis/2., 90., 270., fc='white', edgecolor='black')
        if phase_angle <= 268.: # waning gibbous
            ell1 = Ellipse((0,0), minor_axis, major_axis, fc=c1, edgecolor=c1)
    #               270:  minor  = 0.  Last Quarter    (left: white, right: black, half-ellipse: n/a really)
    #           270-360:  minor  > 0.  Waning Crescent (left: white, right: black, half-ellipse: black)
        if phase_angle >= 272 and phase_angle < 358.:
            ell1 = Ellipse((0,0), minor_axis, major_axis, fc=c0, edgecolor=c0) 

    # put in the wedges
    if wed1: 
        ax.add_artist(wed1)
    if wed2:
        ax.add_artist(wed2)
    # on top of that, the ellipse
    if ell1:
        ax.add_patch(ell1)
    # or the circle
    if cir1:
        ax.add_patch(cir1)
    # and for consistency, the red circle...
    circle2 = plt.Circle((0,0), ang_size_radians/2., color='r', fill=False)
    ax.add_patch(circle2)
    return ax

def map_whole_planet(ax, ang_size_radians):
    """
    For superior planets (esp. Mars) we COULD generate a phased image.
    But for now, we won't.
    """
    circle1 = plt.Circle((0,0), ang_size_radians/2., color='w')
    ax.add_patch(circle1)
    circle2 = plt.Circle((0,0), ang_size_radians/2., color='r', fill=False)
    ax.add_patch(circle2)
    return ax

def map_saturn_rings(ax, planet, t0):
    """
    Given the tilt of the rings as seen from Earth, superimpose them on the disk.
        - 0.665 is the fractional radius of the inner edge of the inner ring.
    You'll immediately notice that I'm just putting down two ellipses and the 
    disk atop it.   Sue me.  :-)

    TODO: make this more realistic
        - use arcs to simulate the 3-dness of things
        - test against the vector of the pole of Saturn's rotation...
    """
    rings = saturn_ring(t0, planet['target'])
    a = math.radians(rings['major'] / 3600.)
    b = math.radians(rings['minor'] / 3600.)
    
    # Outer edge of the rings
    re1 = Ellipse((0,0), a, b, fill=False)
    ax.add_patch(re1)
    # Inner edge of the rings
    re2 = Ellipse((0,0), a*.665, b*.665, fill=False)
    ax.add_patch(re2)
    return ax

def map_dsos(ax, earth, t, projection, 
        center = None,
        mag_limit=None, dso=None, priority=5, color='black', alpha=1
    ):
    """
    Like the star mapping methods above, put down symbols for DSOs.

    TODO: I THINK We want to ALWAYS send a center value, even when this is
        called from create_planet_image or plot_track because then we ought
        to be able to make things run faster.
    """
    other_dso_records = DSO.objects.all()

    # Filter the set
    if mag_limit: # exclude faint objects off the top
        other_dso_records = other_dso_records.exclude(magnitude__gte=mag_limit)
    if dso: # if I'm a DSO finder chart, exclude myself
        other_dso_records = other_dso_records.exclude(pk = dso.pk)

    # Winnow the list:
    # Priorities are Highest, High, Medium, Low, and None, ranked 1 to 5.
    # Cull the list based on priority:
    #   A. DSO Finder charts want everything shown, so the default priority is set
    #       to something > 4 so that everything shows up.
    #   B. Skymap, however, only wants the highest priority DSOs so as not to 
    #       overwhelm the chart.
    #   C. Other custom calls could have something in-between
    #       TODO: Create this functionality!
    #
    if priority <= 4:
        other_dso_records = other_dso_records.exclude(priority='None')
    if priority <= 3:
        other_dso_records = other_dso_records.exclude(priority='Low')
    if priority <= 2:
        other_dso_records = other_dso_records.exclude(priority='Medium')
    if priority <= 1:
        other_dso_records = other_dso_records.exclude(priority='High')

    # Create the plotting dictionary
    other_dsos = {'x': [], 'y': [], 'label': [], 'marker': []}
    interesting = []
    # Loop through the culled DSO list, add to interesting.
    for other in other_dso_records:
        if center: # how far away am I from the center?
            sin_dist = get_altitude(center[0], center[1], other.ra, other.dec)
            if sin_dist < 0: # if the sine of the distance angle is <0 we're below the horizon
                continue
            else: # Oooh - I'm a contender
                interesting.append(other)
        x, y = projection(earth.at(t).observe(other.skyfield_object))
        other_dsos['x'].append(x)
        other_dsos['y'].append(y)
        other_dsos['label'].append(other.shown_name)
        other_dsos['marker'].append(other.object_type.marker_type)
    xxx = np.array(other_dsos['x'])
    yyy = np.array(other_dsos['y'])
    mmm = np.array(other_dsos['marker'])
    # On the Sky Map, we don't show the scaled DSO and custom markers, e.g., 
    #   rotated ellipses for galaxies.
    # Instead we just have some marker symbols.
    # Matplotlib needs us to overlay each set of those marker symbols individually (sigh)
    unique_markers = set(mmm) 
    for um in unique_markers:
        mask = mmm == um # note = then == !
        ax.scatter(
            xxx[mask], yyy[mask],
            s=90., edgecolor='g', facecolors='none',
            marker=um, alpha=alpha
        )
    # Add labels
    for x, y, z in zip(xxx, yyy, other_dsos['label']):
        ax.annotate(
            z, xy=(x,y),
            xytext=(5, 5),
            textcoords='offset points',
            horizontalalignment='left',
            annotation_clip = True,
            color=color
        )
    return ax, interesting


def map_planets(ax, this_planet, planets, earth, t, projection, center=None):
    """
    Sometimes, planets sneak into the finder charts, esp. close conjunctions!
    So, let's put in the other planets too.
    """
    d = {'x': [], 'y': [], 'marker': []}
    planet_labels = []
    interesting = []
    for k,v in planets.items():
        if k == this_planet:
            continue
        ra = v['coords']['ra']
        dec = v['coords']['dec']
        if center:
            sin_dist = get_altitude(center[0], center[1], ra, dec)
            if sin_dist < 0.: # skip the rest of processing.
                continue
            else:
                interesting.append(v)
        x, y = projection(earth.at(t).observe(Star(ra_hours=ra, dec_degrees=dec)))
        d['x'].append(x)
        d['y'].append(y)
        d['marker'].append(UNICODE[k])
    xxx = np.array(d['x'])
    yyy = np.array(d['y'])
    mmm = np.array(d['marker'])
    for x, y, z in zip(xxx, yyy, mmm):
        ax.annotate (
            z, xy=(x, y),
            textcoords='offset points',
            xytext=(0,0),
            horizontalalignment='center',
            color='fuchsia',
            fontsize=20
        )
    return ax, interesting

def map_asteroids(ax, asteroid_list, utdt, projection, center=None, size=60, color='maroon', marker='o', alpha=0.8):
    adict = { 'x': [], 'y': [], 'label': []}
    interesting = []
    for a in asteroid_list:
        if center:
            sin_dist = get_altitude(center[0], center[1], a['coords']['ra'], a['coords']['dec'])
            if sin_dist < 0.:
                continue # skip the rest of processing
            else:
                interesting.append(a)
        x, y = projection(a['target'])
        adict['x'].append(x)
        adict['y'].append(y)
        adict['label'].append(a['object'].number)
    scatter = ax.scatter(
        adict['x'], adict['y'], 
        s=size, c=color, 
        marker=marker, alpha=alpha
    )
    for x, y, z in zip(adict['x'], adict['y'], adict['label']):
        fsize = 6 if len(str(z)) <= 2 else 5
        dy = -3 if len(str(z)) <=2 else -2
        ax.annotate(
            z, xy=(x,y),
            textcoords='offset points',
            xytext=(0,dy),
            horizontalalignment='center',
            color='white',
            fontsize=fsize
        )
    return ax, interesting

def map_single_object(ax, name, obj, earth, t, projection, color='silver'):
    """
    Put in the Sun and Moon Unicode symbols on the map.

    TODO: replace the Moon's unicode with a scaled Moon phase.
    """
    ra, dec, dist = obj['target'].radec()
    x, y = projection(
        earth.at(t).observe(
            Star(
                ra_hours=ra.hours.item(), 
                dec_degrees=dec.degrees.item()
            )
        )
    )
    m = UNICODE[name]
    ax.annotate(
        m, xy=(x,y),
        textcoords='offset points',
        xytext=(0,0),
        horizontalalignment='center',
        color=color,
        fontsize=20
    )
    return ax

def map_meteor_showers(ax, utdt, earth, t, projection, 
        center=None,
        color='c', marker='x', size=150, alpha=1.0):
    """
    Show meteor showers on the map with a big cyan X.
    """    
    active = get_meteor_showers(utdt=utdt)
    if len(active) == 0: # Nothing to do!
        return ax, None

    d = {'x': [], 'y': [], 'label': [], 'marker': []}
    interesting = []
    for a in active:
        if center:
            sin_dist = get_altitude(center[0], center[1], a.radiant_ra, a.radiant_dec)
            if sin_dist < 0.:
                continue
            else:
                interesting.append(a)
        x, y = projection(earth.at(t).observe(a.skyfield_object))
        d['x'].append(x)
        d['y'].append(y)
        d['label'].append(a.name)

    scatter = ax.scatter(
        d['x'], d['y'], 
        s=size, c=color, 
        marker=marker, alpha=alpha
    )
    return ax, interesting

def map_comets(ax, utdt, earth, t, projection,
        center = None, comet_mag_limit = 12.0,
        color='#cc0', marker='h', size=60, alpha=1.0):

    alpha_list = 'ABCDEFGH'
    n = 0
    comets = Comet.objects.filter(status=1)
    d = {'x': [], 'y': [], 'label': [], 'marker': []}
    interesting = []
    for c in comets:
        obs = get_comet(utdt, c)
        mag = obs['observe'].get('apparent_mag', 99)
        if mag > comet_mag_limit:
            continue # too faint - keep going
        #if obs is None:
        #    continue
        ra = obs['coords']['ra']
        dec = obs['coords']['dec']
        if center:
            sin_dist = get_altitude(center[0], center[1],ra, dec)
            if sin_dist < 0.:
                continue
            interesting.append(c)
        x, y = projection(earth.at(t).observe(
            Star(ra_hours=ra,dec_degrees=dec)
        ))
        d['x'].append(x)
        d['y'].append(y)
        d['label'].append(alpha_list[n])
        n += 1

    scatter = ax.scatter(
        d['x'], d['y'],
        s=size, c=color,
        marker=marker, alpha=alpha
    )
    for x, y, z in zip(d['x'], d['y'], d['label']):
        fsize = 6
        dy = -3
        print ("X: ", x, "Y: ", y, "Z: ", z)
        ax.annotate(
            z, xy=(x,y),
            textcoords='offset points',
            xytext=(0,dy),
            horizontalalignment='center',
            color='black',
            fontsize=fsize
        )
    return ax, interesting