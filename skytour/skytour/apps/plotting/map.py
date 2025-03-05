import math
import matplotlib
import numpy as np
from matplotlib import pyplot as plt
from matplotlib.collections import LineCollection
from matplotlib.patches import Wedge, Ellipse
from skyfield.api import Star, load
from skyfield.data import hipparcos, stellarium

from ..astro.astro import get_altitude
from ..astro.markers import generate_equator, SPECIAL_POINTS
from ..dso.atlas_utils import assemble_neighbors, find_neighbors
from ..dso.milky_way import get_list_of_segments
from ..dso.models import DSO
from ..site_parameter.helpers import find_site_parameter
from ..solar_system.meteors import get_meteor_showers
from ..solar_system.saturn import saturn_ring
from ..solar_system.vocabs import UNICODE
from ..stars.models import BrightStar
from ..stars.vocabs import CONSTELLATION_LABELS

matplotlib.use('Agg') # This gets around some of Matplotlib's oddities

"""
Each of the methods create a piece of a map.
Each takes the matplotlib.Axes object instance (ax), does some operation,
and returns it "back" to whatever is assembling the plot.
"""

def map_constellation_lines(ax, stars, reversed=False, line_color=None):
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
    if line_color is None:
        line_color = '#99f8' if reversed else '#00f2' 
    ax.add_collection(LineCollection(lines_xy, colors=line_color))
    return ax

def new_map_constellation_boundaries(ax, lines, earth, t, projection, reversed=False):
    """
    Map the constellation boundaries.
    """
    line_color = '#9907' if reversed else '#999' # constellation-boundary
    line_width = 1.5
    line_type = '--'
    for k, v in lines.items():
        # k is the key, v is the list of coordinates
        d = dict(x =[], y = [])
        for point in v:
            ra = point[0]
            dec = point[1]
            x, y = projection(earth.at(t).observe(Star(ra_hours=ra, dec_degrees=dec)))
            d['x'].append(x)
            d['y'].append(y)
        w = ax.plot(d['x'], d['y'], ls=line_type, lw=line_width, alpha=0.7, color=line_color)
    return ax

def map_hipparcos(ax, earth, t, mag_limit, projection, mag_offset=0.25, reversed=False):
    """
    Put down sized points for stars.
    While this DOES pre-filter by mag_limit it does NOT filter
    by proximity to the center of the map and its scale!
    """
    with load.open(hipparcos.URL) as f:
        stars = hipparcos.load_dataframe(f)
    # Compute the X,Y coordinates of stars on the plot
    star_positions = earth.at(t).observe(Star.from_dataframe(stars))
    stars['x'], stars['y'] = projection(star_positions)
    bright_stars = (stars.magnitude <= mag_limit)
    magnitude = stars['magnitude'][bright_stars]
    marker_size = (mag_offset + mag_limit - magnitude) **2.0 
    ##### background stars
    star_color = 'w' if reversed else 'k'
    scatter = ax.scatter(
        stars['x'][bright_stars], stars['y'][bright_stars], 
        s=marker_size, color=star_color
    )
    return ax, stars

def map_bright_stars(ax, earth, t, projection, 
        mag_limit=None, points=True, annotations=True, reversed=False
    ):
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
        Star(ra_hours=ra, dec_degrees=dec))
    )
    object_scatter = ax.scatter(
        [object_x], [object_y], 
        s=[90.], c=['#900'], 
        marker='+'
    )
    return ax

def map_eyepiece(ax, diam=None, color=None, reversed=False, equinox=True):
    """
    the default is 1° FOV.
    """
    diam = find_site_parameter('eyepiece-fov', default=60., param_type='float')
    radius = math.radians(diam/ 60. / 2. / 2.) # if diam is not None else fov * 2.909e-4 / 2.
    circle_color = 'c' if reversed else 'b'
    eyepiece = plt.Circle((0,0), radius, color=circle_color, fill=False)
    ax.add_patch(eyepiece)
    # Equinox
    if equinox:
        width = 47. * 2.909e-4 / 2.
        height = 34. * 2.909e-4 / 2.
        x0 = -width / 2.
        y0 = -height / 2.
        rect1 = plt.Rectangle((x0, y0), width, height, color='#f00', fill=False)
        ax.add_patch(rect1)
    return ax

def map_circle(ax, diam=None, center=None, reversed=False, color=None):
    if diam is None:
        return ax
    radius = math.radians(diam/60./2./.2)
    if color is None:
        color = '#333' if reversed else '#ccc'
    if center is None:
        center = (0,0)
    else:
        pass
    
    circ = plt.Circle((0,0), radius, color=color, fill=False)
    ax.add_patch(circ)
    return ax

def map_moons(ax, pdict, earth, t, projection, ang_size_radians, reversed=False, debug=False):
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
    dist_to_planet = pdict['apparent']['distance']['au']
    planet_ra = pdict['apparent']['equ']['ra']
    planet_dec = pdict['apparent']['equ']['dec']
    planet_target = earth.at(t).observe(Star(ra_hours=planet_ra, dec_degrees=planet_dec))
    max_sep = 0.
    try:
        for moon in pdict['moons']:
            moon_ra = moon['apparent']['equ']['ra']
            moon_dec = moon['apparent']['equ']['dec']
            d = moon['apparent']['distance']['au']
            moon_target = earth.at(t).observe(Star(ra_hours=moon_ra, dec_degrees=moon_dec))
            sep = moon_target.separation_from(planet_target).radians
            x, y = projection(moon_target)
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
        moon_color = 'c' if reversed else 'b'
        moon_scatter = ax.scatter(moon_pos_list['x'], moon_pos_list['y'], color=moon_color, marker='+')
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
    if phase_angle < 2. or phase_angle > 358.0: # New Moon
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

def map_whole_planet(ax, ang_size_radians, reversed=False):
    """
    For superior planets (esp. Mars) we COULD generate a phased image.
    But for now, we won't.
    """
    disk_color = '#ccc' if reversed else 'w'
    circle1 = plt.Circle((0,0), ang_size_radians/2., color=disk_color)
    ax.add_patch(circle1)
    circle2 = plt.Circle((0,0), ang_size_radians/2., color='r', fill=False)
    ax.add_patch(circle2)
    return ax

def map_saturn_rings(ax, pdict, t0, reversed=False):
    """
    Given the tilt of the rings as seen from Earth, superimpose them on the disk.
        - 0.665 is the fractional radius of the inner edge of the inner ring.
    You'll immediately notice that I'm just putting down two ellipses and the 
    disk atop it.   Sue me.  :-)

    TODO: make this more realistic
        - use arcs to simulate the 3-dness of things
        - test against the vector of the pole of Saturn's rotation...
    """
    rings = saturn_ring(t0, pdict)
    a = math.radians(rings['major'] / 3600.)
    b = math.radians(rings['minor'] / 3600.)
    
    # Outer edge of the rings
    ring_color = 'w' if reversed else 'k'
    re1 = Ellipse((0,0), a, b, fill=False, color=ring_color)
    ax.add_patch(re1)
    # Inner edge of the rings
    re2 = Ellipse((0,0), a*.665, b*.665, fill=False, color=ring_color)
    ax.add_patch(re2)
    return ax

def map_dsos(ax, earth, t, projection, 
        center = None,
        dso=None, 
        dso_list=None,
        alpha=1,
        label_size = None,
        symbol_size = 40., # was 90
        reversed=False,
        ignore_setting = False, # for Skymap, not finder charts
        product = 'skymap',
        label_weight = 'bold',
        colors=None,
        sort_list=True,
        min_alt = 20. # degrees
    ):
    """
    Like the star mapping methods above, put down symbols for DSOs.

    TODO: I THINK We want to ALWAYS send a center value, even when this is
        called from create_finder_chart or plot_track because then we ought
        to be able to make things run faster.

    TODO: IF you are creating a plot that has a center + radius or FOV, 
        then you can change the sin(altitude) to be > 0, i.e., the sin(90 - radius)
        or sin(90 - fov/2)...   I think.
    """
    if dso_list is not None:
        other_dso_records = dso_list
    elif dso: # if I'm a DSO finder chart, exclude myself
        other_dso_records = other_dso_records.exclude(pk = dso.pk)
    elif product == 'skymap':
        other_dso_records = DSO.objects.filter(show_on_skymap=1).order_by('ra_text')
    else:
        other_dso_records = DSO.objects.order_by('ra_text')

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
                if not ignore_setting:
                    interesting.append(other)
                else:
                    my_alt = math.degrees(math.asin(sin_dist))
                    if my_alt > min_alt:
                        interesting.append(other)
        x, y = projection(earth.at(t).observe(other.skyfield_object))
        other_dsos['x'].append(x)
        other_dsos['y'].append(y)
        other_dsos['label'].append(other.label_on_chart)
        other_dsos['marker'].append(other.object_type.marker_type)
    xxx = np.array(other_dsos['x'])
    yyy = np.array(other_dsos['y'])
    mmm = np.array(other_dsos['marker'])

    # On the Sky Map, we don't show the scaled DSO and custom markers, e.g., 
    #   rotated ellipses for galaxies.
    # Instead we just have some marker symbols.
    # Matplotlib needs us to overlay each set of those marker symbols individually (sigh)
    unique_markers = set(mmm)
    if product != 'atlas':
        dso_color = '#9f9' if reversed else 'g'
    else:
        dso_color = 'c' if reversed else 'b'
    for um in unique_markers:
        mask = mmm == um # note = then == !
        if um != 'x':
            ax.scatter(
                xxx[mask], yyy[mask],
                s=symbol_size, edgecolor=dso_color, facecolors='none',
                marker=um, alpha=alpha
            )
        else:
            ax.scatter(
                xxx[mask], yyy[mask],
                s=symbol_size, facecolors='none',
                marker=um, alpha=alpha
            )
    # Add labels
    if colors is None:
        if product != 'atlas':
            color = '#cc0' if reversed else '#666'
        else:
            color = '#6ff' if reversed else '#333'
    else:
        color = colors[1] if reversed else colors[0]

    for x, y, z in zip(xxx, yyy, other_dsos['label']):
        ax.annotate(
            z, xy=(x,y),
            xytext=(5, 5),
            textcoords='offset points',
            horizontalalignment='left',
            annotation_clip = True,
            color=color,
            fontsize=label_size,
            fontweight=label_weight
        )
    if sort_list:
        zz = sorted(interesting, key=lambda t: (t.catalog.abbreviation, t.id_in_catalog))
        interesting = zz
    return ax, interesting


def map_planets(ax, this_planet, planets, earth, t, projection, center=None):
    """
    Sometimes, planets sneak into the finder charts, esp. close conjunctions!
    So, let's put in the other planets too.
    """
    d = {'x': [], 'y': [], 'marker': []}
    interesting = []
    for k, v in planets.items():
        if k == this_planet: # Skip me
            continue
        ra = v['apparent']['equ']['ra']
        dec = v['apparent']['equ']['dec']
            
        if center: # Used for Skymap
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

def map_asteroids(ax, name, asteroid_list, earth, t, projection, 
        center=None, size=60, marker='o', alpha=0.8,
        reversed=False
    ):
    adict = { 'x': [], 'y': [], 'label': []}
    interesting = []
    for a in asteroid_list:
        ra = a['apparent']['equ']['ra']
        dec = a['apparent']['equ']['dec']
        if name == a['name']:
            continue # don't map myself!
        if center:
            sin_dist = get_altitude(center[0], center[1], ra, dec)
            if sin_dist < 0.:
                continue # skip the rest of processing
            else:
                interesting.append(a)
        x, y = projection(earth.at(t).observe(Star(ra_hours=ra, dec_degrees=dec)))
        adict['x'].append(x)
        adict['y'].append(y)
        adict['label'].append(a['number'])
    asteroid_color = 'red' if reversed else 'maroon'
    scatter = ax.scatter(
        adict['x'], adict['y'], 
        s=size, c=asteroid_color, 
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
    ra = obj['apparent']['equ']['ra']
    dec = obj['apparent']['equ']['dec']
    x, y = projection(earth.at(t).observe(Star(ra_hours=ra, dec_degrees=dec)))
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
        color='c', marker='x', size=150, alpha=1.0,
        reversed=True
    ):
    """
    Show meteor showers on the map with a big X.
    """    
    active = get_meteor_showers(utdt=utdt)
    if len(active) == 0: # Nothing to do!
        return ax, None

    d = {'x': [], 'y': [], 'label': [], 'marker': [], 'size': []}
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
        if a.intensity == 'Major':
            d['size'].append(size)
        elif a.intensity == 'Minor':
            d['size'].append(size * 0.5)
        else:
            d['size'].append(size * 0.25)


    scatter = ax.scatter(
        d['x'], d['y'], 
        s=d['size'], c=color, 
        marker=marker, alpha=alpha
    )
    return ax, interesting

def map_comets(ax, comet_list, earth, t, projection,
        center = None, comet_mag_limit = 12.0,
        color='#f0e090', marker='h', size=60, alpha=1.0,
        reversed=True
    ):

    alpha_list = 'ABCDEFGHJKLMNPQRSTUVWXYZ' # No I or O
    n = 0
    d = {'x': [], 'y': [], 'label': [], 'marker': []}
    interesting = []
    for c in comet_list:
        ra = c['apparent']['equ']['ra']
        dec = c['apparent']['equ']['dec']
        if center:
            sin_dist = get_altitude(center[0], center[1],ra, dec)
            if sin_dist < 0.:
                continue
            c['letter'] = alpha_list[n]
            interesting.append(c)
        x, y = projection(earth.at(t).observe(Star(ra_hours=ra,dec_degrees=dec)))
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
        ax.annotate(
            z, xy=(x,y),
            textcoords='offset points',
            xytext=(0,dy),
            horizontalalignment='center',
            color='black',
            fontsize=fsize
        )
    return ax, interesting


def map_equ(ax, earth, t, projection, type, reversed=False):
    if type == 'equ':
        points = generate_equator()
        line_type = (0, (7, 10))
        color = '#f9f' if reversed else '#f99' # lines, equator
    elif type == 'ecl':
        points = generate_equator(type='ecl')
        line_type = '-.'
        color = '#6ff' if reversed else '#3c3' # lines, ecliptic
    elif type == 'gal':
        points = generate_equator(type='gal')
        line_type = '--' # (0, (3, 5, 1, 5, 1, 5))
        color = '#c6f' # lines, galactic
    else:
        return ax

    d = dict(x = [], y = [])
    for p in points:
        ra, dec = p
        xx, yy = projection(earth.at(t).observe(Star(ra_hours=ra, dec_degrees=dec)))
        d['x'].append(xx)
        d['y'].append(yy)
    w = ax.plot(d['x'], d['y'], ls=line_type, lw=1., alpha=0.7, c=color)
    return ax

def map_milky_way(
        ax, earth, t, projection, 
        contour=1, 
        # center_ra=None, center_dec=None, radius=None,
        reversed=False,
        line_width = 2.,
        alpha = 0.7,
        colors = ['#099', '#fc0'],
    ):
    color = colors[1] if reversed else colors[0]
    line_type = (0, (1,1))
    segments = get_list_of_segments(contour=contour)
    for segment in segments:
        d = {'x': [], 'y': []}
        for coord in segment:
            xx, yy = projection(earth.at(t).observe(Star(ra_hours=coord[0], dec_degrees=coord[1])))
            # TODO: test if xx, yy near the plot to speed this up
            d['x'].append(xx)
            d['y'].append(yy)
        w = ax.plot(d['x'], d['y'], c=color, ls=line_type, lw=line_width, alpha=alpha)
    return ax

def map_special_points(ax, earth, t, projection, 
        marker='x', 
        size=150, 
        reversed=False,
        alpha = 0.8,
        colors = ['#fa0', '#fa0']
    ):
    d = {'x': [], 'y': [], 'label': [], 'marker': []}

    for a in SPECIAL_POINTS:
        x, y = projection(earth.at(t).observe(Star(ra_hours=a['ra'], dec_degrees=a['dec'])))
        d['x'].append(x)
        d['y'].append(y)
        d['label'].append(a['abbr'])

    color = colors[1] if reversed else colors[0] # special-points, symbol
    scatter = ax.scatter(
        d['x'], d['y'], 
        s=size, c=color, 
        marker=marker, alpha=alpha
    )
    tcolor = '#ccc' if reversed else '#666' # special-points, label
    for x, y, z in zip(d['x'], d['y'], d['label']):
        ax.annotate(
            z, xy=(x,y),
            textcoords='offset points',
            xytext=(10, -10),
            horizontalalignment='center',
            color=tcolor,
            fontsize=6,
            style='italic'
        )
    return ax

def map_plate_neighbors(ax, plate, reversed=reversed):
    rows = assemble_neighbors(find_neighbors(plate.center_ra, plate.center_dec))
    neighbors = []
    row_number = 0
    for row in rows:
        p_num = 0
        for n in row:
            p_num += 1
            if n['sep'] < 0.1: # skip center
                continue
            if len(row) == 5 and p_num not in [2,4]: # deal with dec 75 issue
                continue
            neighbors.append(n)
        row_number += 1

    csize = math.radians(.25)
    radius = math.radians(9.2/2.)
    d = {'x': [], 'y': [], 't': []}
    tcolor = '#777' if reversed else '#fff' # atlas-plate-reference, label
    fcolor = '#444' if reversed else '#ccc' # atlas-plate-reference, background

    for n in neighbors:
        pa = math.radians(n['pa'] - 90.)
        text = n['plate']
        plate_id = int(text)
        if plate_id == 1:
            pa = math.radians(90.)
        elif plate_id == 258:
            pa = math.radians(-90.)
        x = radius * math.cos(pa)
        y = radius * math.sin(pa)
        d['x'].append(x)
        d['y'].append(y)
        d['t'].append(text)

    for x, y, z in zip(d['x'], d['y'], d['t']):
        c = plt.Circle((x,y), csize, color=fcolor, fill=True, alpha=0.7)
        ax.add_patch(c)
        ax.annotate(z, xy=(x, y), 
            color=tcolor, fontsize=12, 
            verticalalignment='center',
            horizontalalignment='center'
        )
    return ax

def map_constellation_names(ax, plate, earth, t, projection, reversed=reversed):
    constellations = plate.atlasplateconstellationannotation_set.all()
    d = {'x': [], 'y': [], 'label': []}
    tcolor = '#ffb' if reversed else '#333'  # constellation, markers, label
    fcolor = '#333' if reversed else '#fff'  # constellation, markers, background
    ecolor = '#ffd' if reversed else '#000'  # constellation, markers, edge
    for c in constellations:
        x, y = projection(earth.at(t).observe(Star(ra_hours=c.ra, dec_degrees=c.dec)))
        d['x'].append(x)
        d['y'].append(y)
        d['label'].append(c.constellation.abbreviation)
    for x, y, z in zip(d['x'], d['y'], d['label']):
        ax.text(x, y, z, color=tcolor, fontsize='x-small',
            bbox = dict(
                facecolor=fcolor, 
                edgecolor=ecolor,
                pad=1.0
            )
        )
    return ax

def map_constellation_labels(ax, earth, t, projection):
    d = {'x': [], 'y': [], 'label': []}
    for k in CONSTELLATION_LABELS.keys():
        ra, dec = CONSTELLATION_LABELS[k]
        #ra = v[0]
        #dec = v[1]
        x, y = projection(earth.at(t).observe(Star(ra_hours=ra, dec_degrees=dec)))
        if abs(x) > 1 or abs(y) > 1:
            continue
        #print(f"K: {k} X: {x} Y: {y}")
        d['x'].append(x)
        d['y'].append(y)
        d['label'].append(k)
    for x, y, z in zip(d['x'], d['y'], d['label']):
        ax.text(x, y, z, color='#9009', fontsize='x-small', 
            fontstyle='italic', ha='center', va='center',
            bbox = dict(facecolor='#FFF', edgecolor='#fff', pad=1.0)
        )
    return ax
        
def map_mask(ax, location, color='#3ff', simple=False, debug=False):
    n = 0

    def get_xy(az, alt):
        rad = (90 - alt)/90.
        x = rad * math.cos(math.radians(az+90.))
        y = rad * math.sin(math.radians(az+90.))
        return x, y
    
    def add_mask_points(mask, x, y, steps = 10):
        points = []
            
        for i in range(steps+1):
            z = (i + 0.)/steps
            dx = mask.azimuth_start + z * (mask.azimuth_end - mask.azimuth_start)
            dh = mask.altitude_end - mask.altitude_start
            dy = mask.altitude_start + z * dh
            if i != 0:
                x0, y0 = get_xy(x, y)
                x1, y1 = get_xy(dx, dy)
                ax.plot([x0, x1], [y0, y1], color=color, linewidth=2)
                if debug:
                    point = ((x, y), (dx, dy))
                    print(f"\t{i}: Sub arc: {point}")
            x = dx
            y = dy
        return
            
    prev_mask = None
    for mask in location.observinglocationmask_set.order_by('azimuth_start'):
        if prev_mask: # connect two segments
            x0, y0 = get_xy(prev_mask.azimuth_end, prev_mask.altitude_end)
            x1, y1 = get_xy(mask.azimuth_start, mask.altitude_start)
            ax.plot([x0, x1], [y0, y1], color=color, linewidth=2)
            x = x1
            y = y1
            if debug:
                point = (
                    (prev_mask.azimuth_end, mask.altitude_end), 
                    (prev_mask.azimuth_start, mask.altitude_start)
                )
                print(n, "Adding Mask from Prev: ", point)
        else:
            first_mask = mask

        if simple: # add new segment
            x0, y0 = get_xy(mask.azimuth_start, mask.altitude_start)
            x1, y1 = get_xy(mask.azimuth_end, mask.altitude_end)
            ax.plot([x0, x1], [y0, y1], color=color, linewidth=2)
            if debug:
                point = ((mask.azimuth_start, mask.altitude_start), (mask.azimuth_end, mask.altitude_end))
                print(n, "Adding Mask from Mask: ", mask)
        else:
            add_mask_points(mask, mask.azimuth_start, mask.azimuth_end)

        prev_mask = mask
        n += 1

    # final point
    ax.plot([mask.azimuth_end, first_mask.azimuth_start], [mask.altitude_end, first_mask.altitude_start], color=color, linewidth=2)
    if debug:
        point = (
            (mask.azimuth_end, mask.altitude_end),
            (mask.azimuth_start, first_mask.altitude_start)
        )
        print(n, "Adding Last Point: ", mask)
    
    return ax