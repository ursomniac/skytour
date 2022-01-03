import base64
import datetime
import io
import math
import matplotlib
import numpy as np

from matplotlib import pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.patches import Wedge, Ellipse
from skyfield.api import load, Star
from skyfield.projections import build_stereographic_projection

from ..observe.time import get_t_epoch, get_julian_date
from ..plotting.map import *
from .planets import get_solar_system_object

matplotlib.use('Agg') # this gets around the threading issues.

def create_planet_image(
        planet, # dict from get_solar_system_object() - can also be the Moon
        utdt, # UTDT 
        other_planets = None, # show other planets on finder chart
        fov=None, # force the FOV of the image
        mag_limit=8.5, # faintest stars on plot
        figsize=None, # size of plot
        finder_chart=False, # Am I making a eyepiece view or finder chart?
        show_axes=False, # mostly for debugging
        debug=False # print stuff to the console
    ):
    """
    Create the images involving planets:
        - finder chart (useful for Uranus and Neptune, and possibly Mercury)
        - telescope view:
            - phased for inferior planets
            - whole with moon locations for superior planets
    """
    name = planet['name']

    # Set up Skyfield
    ts = load.timescale()
    t = ts.from_datetime(utdt)
    eph = load('de421.bsp')
    earth = eph['earth']
    t0 = get_t_epoch(get_julian_date(utdt))
    
    if name != 'Moon':
        ang_size = planet['observe']['angular_diameter'] # arcsec
        ang_size_radians = math.radians(ang_size/3600.)
    else:
        ang_size = planet['observe']['angular_diameter'] # degrees!
        ang_size_radians = math.radians(ang_size)

    # Start making a plot
    fig, ax = plt.subplots(figsize=[6,6])
    projection = build_stereographic_projection(planet['target'])

    # Call all the methods to plop more things on the plot.
    if finder_chart:
        # Add stars from Hipparcos, constellation lines (from Stellarium),
        #   and Bayer/Flamsteed designations from the BSC
        ax, stars = map_hipparcos(ax, earth, t, mag_limit, projection)
        ax = map_constellation_lines(ax, stars)
        ax = map_bright_stars(ax, earth, t, projection, points=False, annotations=True)

        # Don't plot the planet - just a symbol.
        (planet_ra, planet_dec, planet_dist) = planet['target'].radec()
        ax = map_target(ax, planet_ra, planet_dec, projection, earth, t, '+')

        # Add an eyepiece circle, 32mm eyepiece = 0.0038 radians
        ax = map_eyepiece(ax, diam=0.0038)

        # Add planet symbols (Unicode)
        if other_planets:
            ax = map_planets(ax, name, other_planets, earth, t, projection)

        # Add DSOs
        ax = map_dsos(ax, earth, t, projection)

    # OR put up a telescopic view of the planet with moons, or phases
    else:
        # Add moons
        if 'moons' in planet.keys():
            # return the maximum separation of a moon from its planet.
            # This determines the scale of the view.
            ax, moon_pos_list, max_sep = map_moons(ax, planet, earth, t, projection, ang_size_radians)
            for x, y, z, o in zip(moon_pos_list['x'], moon_pos_list['y'], moon_pos_list['label'], moon_pos_list['o']):
                plt.annotate(z, (x, y), textcoords='offset points', xytext=(0, o), ha='center') 
        else: # no moons, set max_sep to 3*ang_size of the planet.
            max_sep = 3 * ang_size_radians

        # If Saturn, add rings
        # TODO: deal with having the ring in front of the planet and then behind it.
        if name == 'Saturn':
            ax = map_saturn_rings(ax, planet, t0)

        # Moon and inferior planets have phases!
        if name in ['Moon', 'Mercury', 'Venus']:
            ax = map_phased_planet(ax, planet, ang_size_radians)
        else: # just a regular disk for superior planets
            ax = map_whole_planet(ax, ang_size_radians)

    # Plot scaling
    # THIS IS WAY MORE COMPLICATED THAN IT OUGHT TO BE.
    if not fov: # set FOV if not supplied
        if finder_chart:
            fov = 8. if planet['name'] in ['Uranus', 'Neptune'] else 20.
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
    # This is an unresolved WTF bug --- I don't know why the math gets weird here.
    foo = 2. * limit * 180. / np.pi 
    if finder_chart:
        foo *= 2.
    if debug:
        print("NAME: ", name, "FOV: ", fov, "ANGLE: ", angle, "LIMIT: ", limit, "FOO: ", foo)
    
    ax.set_xlim(-limit, limit)
    ax.set_ylim(-limit, limit)
    ax.xaxis.set_visible(show_axes)
    ax.yaxis.set_visible(show_axes)

    # TODO: Test this because I think it's off by x2
    if foo > 1.2: # more than 1 degree -ish
        fov_str = "{:.1f}°".format(foo) # show degrees
    else:
        fov_str = "{:.1f}\'".format(foo*60.) # show arcminutes

    chart_type = 'Finder Chart' if finder_chart else 'View'
    title = "{} {}  FOV = {}".format(name, chart_type, fov_str)
    ax.set_title(title)

    # Convert to a PNG image
    pngImage = io.BytesIO()
    FigureCanvas(fig).print_png(pngImage)
    # Encode PNG to Base64 string
    pngImageB64String = 'data:image/png;base64,'
    pngImageB64String += base64.b64encode(pngImage.getvalue()).decode('utf8')

    # close things
    plt.cla()
    plt.close(fig)
    return pngImageB64String

### TESTING
# This just exists as an easy way to get to the image and planet metadata.
def ptest(name, utdt=None, fov=None, figsize=None, finder_chart=False, show_axes=False):
    if not utdt:
        utdt = datetime.datetime.now(datetime.timezone.utc)
    if not figsize:
        figsize = [5,5]
    planet = get_solar_system_object(utdt, name)

    #print("PLANET: ", planet)
    image = create_planet_image(name, planet, utdt, fov=fov, mag_limit=9., figsize=figsize, finder_chart=finder_chart, show_axes=show_axes)
    return planet