import base64
import datetime
import io
import math
import matplotlib
import numpy as np
import pytz

from matplotlib import pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.collections import LineCollection
from matplotlib.patches import Wedge, Ellipse

from skyfield.api import Star, load
from skyfield.data import hipparcos, stellarium #, mpc
from skyfield.projections import build_stereographic_projection

from ..meeus.almanac import get_t_epoch, get_julian_date
from ..stars.models import BrightStar
from .saturn import saturn_ring
from .utils import get_solar_system_object
from .vocabs import EPHEMERIS

matplotlib.use('Agg')
def create_planet_image(
        name, # name
        planet, # dict from get_solar_system_object()
        utdt, # UTDT 
        fov=None, # force the FOV of the image
        mag_limit=8.5, # faintest stars on plot
        figsize=None, # size of plot
        finder_chart=False,
        show_axes=False,
        debug=False
    ):
    ts = load.timescale()
    t = ts.from_datetime(utdt)
    eph = load('de421.bsp')
    earth = eph['earth']
    t0 = get_t_epoch(get_julian_date(utdt))

    fig, ax = plt.subplots(figsize=[6,6])

    # Center
    projection = build_stereographic_projection(planet['observe'])
    ang_size = planet['physical']['angular_diameter'] # arcsec
    ang_size_radians = math.radians(ang_size/3600.)
    if debug:
        print("ANG SIZE: ", ang_size, "RADIANS: ", ang_size_radians)



    if finder_chart:
    # Constellations
        url = ('https://raw.githubusercontent.com/Stellarium/stellarium/master'
        '/skycultures/western_SnT/constellationship.fab')
        with load.open(url) as f:
            constellations = stellarium.parse_constellations(f)
        edges = [edge for name, edges in constellations for edge in edges]
        edges_star1 = [star1 for star1, star2 in edges]
        edges_star2 = [star2 for star1, star2 in edges]

        # Hipparcos
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
                xytext=(-5, -5),
                ha='right'
            )
        # Don't plot the planet - just a symbol.  This is for finder charts.
        (planet_ra, planet_dec, planet_dist) = planet['observe'].radec()
        object_x, object_y = projection(earth.at(t).observe(Star(ra_hours=planet_ra.hours, dec_degrees=planet_dec.degrees)))
        object_scatter = ax.scatter(
            [object_x], [object_y], 
            s=[90.], c=['#900'], 
            marker='+'
        )
            # Add an eyepiece circle, 32mm = 0.0038 radians
        eyepiece = plt.Circle((0, 0), 0.0038, color='b', fill=False)
        ax.add_patch(eyepiece)

        # assemble constellation lines
        xy1 = stars[['x', 'y']].loc[edges_star1].values
        xy2 = stars[['x', 'y']].loc[edges_star2].values
        lines_xy = np.rollaxis(np.array([xy1, xy2]), 1)
        ##### constellation lines
        ax.add_collection(LineCollection(lines_xy, colors='#00f2'))
    else:
        # Add moons
        if planet['moons']:
            moon_pos_list = {'x': [], 'y': [], 'label': [], 'd': [], 'o': []}
            # Get RA/Dec for each

            dist_to_planet = planet['observe'].distance().au
            max_sep = 0.
            for moon in planet['moons']:
                (moon_ra, moon_dec, moon_dist) = moon['observe'].radec()
                x, y = projection(earth.at(t).observe(Star(ra_hours=moon_ra.hours, dec_degrees=moon_dec.degrees)))
                d = moon_dist.au
                sep = moon['observe'].separation_from(planet['observe']).radians
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

            for x, y, z, o in zip(moon_pos_list['x'], moon_pos_list['y'], moon_pos_list['label'], moon_pos_list['o']):
                plt.annotate(z, (x, y), textcoords='offset points', xytext=(0, o), ha='center') 

        else: # no moons, set max_sep to 3*ang_size
            max_sep = 3 * ang_size_radians


        if name == 'Saturn':
            rings = saturn_ring(t0, planet['observe'])
            a = math.radians(rings['major'] / 3600.)
            b = math.radians(rings['minor'] / 3600.)
            #print ("a: ", a, "b: ", b)
            re1 = Ellipse((0,0), a, b, fill=False)
            ax.add_patch(re1)
            re2 = Ellipse((0,0), a*.665, b*.665, fill=False)
            ax.add_patch(re2)

        if name in ['Mercury', 'Venus']:
            c1 = None
            e1 = None
            w1 = None
            w2 = None

            phase_angle = planet['physical']['plotting_phase'] # in degrees
            major_axis = ang_size_radians  # radius of planet
            minor_axis = abs(math.cos(math.radians(planet['physical']['phase_angle'])) * ang_size_radians)
            #print("Phase: ", phase_angle, 'Major: ', major_axis, 'Minor: ', minor_axis)
            # Circumstances:
            #    phase:  0, 360:  minor  = 1.  New Moon        (left: black, right: black, half-ellipse: n/a really)
            if abs(phase_angle) < 1.: # New Moon
                c1 = plt.Circle((0,0), ang_size_radians/2., color='k') # black disk
            #    phase:   0- 90:  minor  > 0.  Waxing Crescent (left: black, right: white, half-ellipse: black)
            elif phase_angle < 179:
                w1 = Wedge((0,0), major_axis/2., -90., 90., fc='white', edgecolor='black')
                w2 = Wedge((0,0), major_axis/2., 90., 270., fc='black', edgecolor='black')
                if phase_angle <= 89. : # Waxing Crescent
                    e1 = Ellipse((0,0), minor_axis, major_axis, fc='black', edgecolor='black')
            #                90:  minor  = 0.  First Quarter   (left: black, right: white, half-ellipse: n/a really)
            #            90-180:  minor  < 0.  Waxing Gibbous  (left: black, right: white, half-ellipse: white)
                elif phase_angle <= 179 and phase_angle >= 91.:
                    e1 = Ellipse((0,0), minor_axis, major_axis, fc='black', edgecolor='black')
            #               180:  minor = -1.  Full Moon       (left: white, right: white, half-ellipse: n/a really)
  
            elif phase_angle < 181.: 
                c1 = plt.Circle((0,0), ang_size_radians/2., color='w') # white disk
            #           180-270:  minor  < 0.  Waning Gibbous  (left: white, right: black, half-ellipse: white)
            else:
                w1 = Wedge((0,0), major_axis/2., -90., 90., fc='black', edgecolor='black')
                w2 = Wedge((0,0), major_axis/2., 90., 270., fc='white', edgecolor='black')
                if phase_angle <= 269.: # waning gibbous
                    e1 = Ellipse((0,0), minor_axis, major_axis, fc='black', edgecolor='black')
            #               270:  minor  = 0.  Last Quarter    (left: white, right: black, half-ellipse: n/a really)
            #           270-360:  minor  > 0.  Waning Crescent (left: white, right: black, half-ellipse: black)
                if phase_angle >= 271 and phase_angle < 359.:
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
        else: # just a regular disk!
            circle1 = plt.Circle((0,0), ang_size_radians/2., color='w')
            ax.add_patch(circle1)
            circle2 = plt.Circle((0,0), ang_size_radians/2., color='r', fill=False)
            ax.add_patch(circle2)


    # Plot scaling
    if not fov: # set FOV if not supplied
        if finder_chart:
            fov = 8.
        else:
            # set FOV to slightly more than the greatest moon distance
            # if no moons, then against the angular size of the planet
            if max_sep == 0.:
                fov = 0.05
            else:
                multiple = 0.05
                min_fov = 1.0 * math.degrees(2. * max_sep)
                fov = multiple * round((min_fov +multiple/2)/multiple)
        if fov < 0.05:
            fov = 0.05

    angle = np.pi - fov / 360.0 * np.pi
    limit = np.sin(angle) / (1.0 - np.cos(angle))
    ax.set_xlim(-limit, limit)
    ax.set_ylim(-limit, limit)
    ax.xaxis.set_visible(show_axes)
    ax.yaxis.set_visible(show_axes)

    if fov > 60.: # more than 1 degree
        fov_str = "{:.1f}°".format(fov/60.)
    else:
        fov_str = "{:.1f}\'".format(fov)

    chart_type = 'Finder Chart' if not finder_chart else 'View'
    title = "{} {}  FOV = {}".format(name, chart_type, fov_str)
    ax.set_title(title)

    # Convert to a PNG image
    pngImage = io.BytesIO()
    FigureCanvas(fig).print_png(pngImage)
    # Encode PNG to Base64 string
    pngImageB64String = 'data:image/png;base64,'
    pngImageB64String += base64.b64encode(pngImage.getvalue()).decode('utf8')

    plt.cla()
    plt.close(fig)
    return pngImageB64String
    # Save
    #if finder_chart:
    #    fn = 'test_{}_finder.png'.format(name.title())
    #else:
    #    fn = 'test_{}.png'.format(name.title())
    #fig.savefig(fn, bbox_inches='tight')
    #return fn


### TESTING
def ptest(name, utdt=None, fov=None, figsize=None, finder_chart=False, show_axes=False):
    if not utdt:
        utdt = datetime.datetime.now(datetime.timezone.utc)
    if not figsize:
        figsize = [5,5]
    planet = get_solar_system_object(utdt, name)

    #print("PLANET: ", planet)
    image = create_planet_image(name, planet, utdt, fov=fov, mag_limit=9., figsize=figsize, finder_chart=finder_chart, show_axes=show_axes)
    return planet