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
        other_asteroids = None, # show other asteroids in finder chart
        fov=None, # force the FOV of the image
        min_sep = None,
        mag_limit=8.5, # faintest stars on plot
        figsize=None, # size of plot
        finder_chart=False, # Am I making a eyepiece view or finder chart?
        flipped = False, # for SCT there's a flip in RA
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
            ax, _ = map_planets(ax, name, other_planets, earth, t, projection)

        # Add DSOs
        ax, _ = map_dsos(ax, earth, t, projection)

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
        if min_sep and max_sep < min_sep:
            max_sep = min_sep

        # If Saturn, add rings
        # TODO: deal with having the ring in front of the planet and then behind it.
        if name == 'Saturn':
            ax = map_saturn_rings(ax, planet, t0)

        # Moon and inferior planets have phases!
        if name in ['Moon', 'Mercury', 'Venus']:
            ax = map_phased_planet(ax, planet, ang_size_radians)
        else: # just a regular disk for superior planets
            ax = map_whole_planet(ax, ang_size_radians)

    # Add planet symbols (Unicode)
    if other_planets:
        ax, _ = map_planets(ax, name, other_planets, earth, t, projection)
    if other_asteroids:
        ax, _ = map_asteroids(ax, other_asteroids, utdt, projection)

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
    
    if flipped:
        ax.set_xlim(limit, -limit)
    else:
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
    if flipped:
        title += " (flipped)"
    ax.set_title(title)
    if not finder_chart:
        plt.xlabel('ID above + = moon behind planet in orbit;\nID below + = moon in front of planet in orbit')

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

def plot_ecliptic_positions(planets):
    r = [0., ]
    theta = [0., ]
    label = ['Sun', ]
    colors = ['y', 'grey', 'orange', 'blue', 'red', 'pink', 'brown', 'lime', 'cyan']
    fig = plt.figure()
    ax = fig.add_subplot(projection='polar')
    for d in planets:
        r.append(d['distance'])
        theta.append(d['longitude'])
        label.append(d['name'])

    ax.set_xticks = (np.arange(0, 2.*math.pi, math.pi/12.))
    ax.set_ylim(0, 40)
    ax.set_rscale('symlog')
    c = ax.scatter(theta, r, s=40, c=colors)

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

def plot_track(utdt, planet=None, offset_before=-60, offset_after=61, step_days=5, mag_limit=5.5, dsos=True, fov=10):
    """
    Planet is from the Planet model
    utdt is the MIDPOINT date.
    """
    ts = load.timescale()
    eph = load('de421.bsp')
    earth = eph['earth']
    eph_planet = eph[planet.target]
    t = ts.from_datetime(utdt)
    #t0 = get_t_epoch(get_julian_date(utdt))
    projection_midpoint = earth.at(t).observe(eph_planet)
    fig, ax = plt.subplots(figsize=[8,8])
    projection = build_stereographic_projection(projection_midpoint)
    # Build the observation points
    d_planet = dict(x = [], y = [], label = [])
    i = 0
    for dt in range(offset_before, offset_after, step_days):
        this_utdt = utdt + datetime.timedelta(days=dt)
        tt = ts.from_datetime(this_utdt)
        z = earth.at(tt).observe(eph_planet)
        ra, dec, distance = z.radec()

        xx, yy = projection(earth.at(tt).observe(Star(ra_hours=ra.hours, dec_degrees=dec.degrees)))
        d_planet['x'].append(xx)
        d_planet['y'].append(yy)
        lll = "{}/{:2d}".format(this_utdt.month, this_utdt.day) if i%4 == 0 else ''
        d_planet['label'].append(lll)
        i += 1
    print (d_planet['label'])
    w = ax.scatter(d_planet['x'], d_planet['y'], s=90., c='#900', marker='+', alpha=0.7)
    for x, y, l in zip(d_planet['x'], d_planet['y'], d_planet['label']):
        ax.annotate(
            l, xy=(x, y), 
            textcoords='offset points',
            xytext=(5, 5),
            horizontalalignment='left',
            color='orange'
        )
    
    # Add stars from Hipparcos, constellation lines (from Stellarium),
    #   and Bayer/Flamsteed designations from the BSC
    ax, stars = map_hipparcos(ax, earth, t, mag_limit, projection)
    ax = map_constellation_lines(ax, stars)
    ax = map_bright_stars(ax, earth, t, projection, points=False, annotations=True, mag_limit=mag_limit)
    # Add DSOs
    if dsos:
        ax, _ = map_dsos(ax, earth, t, projection)
    
    angle = np.pi - fov / 360.0 * np.pi
    limit = 2. * np.sin(angle) / (1.0 - np.cos(angle))
    ax.set_xlim(-limit, limit)
    ax.set_ylim(-limit, limit)
    ax.xaxis.set_visible(False)
    ax.yaxis.set_visible(False)

    title = "Track for {}".format(planet.name)
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

def get_planet_map(planet, physical):
    #print("Physical: ", physical)
    try:
        angle = physical['omega']
        d_e = physical['d_e']
        if planet.name == 'Jupiter':
            features = physical['features']
            delta_longitude = 0.
            for f in features:
                if f['name'] == 'Great Red Spot':
                    delta_longitude = f['longitude']
            #delta_longitude = physical['red_spot']['delta_longitude']
    except:
        print ("returning None")
        return None, None, None

    plt.rcParams['figure.figsize'] = [10, 5]
    plt.rcParams['figure.autolayout'] = True
    im = plt.imread(planet.planet_map.file)
    fig, ax = plt.subplots()
    if planet.name == 'Jupiter':
        im = ax.imshow(im, extent=[180, -180, -90, 90])
        # OK here's the tricky bit:
        # on the image, the GRS is at x = 170, which corresponds to
        #   9° + 0.05719° * (utdt - datetime(2022, 1, 1)); i.e., # days since the beginning of the year.
        do = angle - delta_longitude
        px = do if angle <= 180 else do - 360.
        py = -d_e
    elif planet.name == 'Mars':
        im = ax.imshow(im, extent=[360, 0, -90, 90])
        px = angle + 360 if angle < 0 else angle
        py = -d_e
    ax.plot([int(px)], [int(py)], 'wP')

    # Plot feature locations:
    ppx = []
    ppy = []
    for feature in physical['features']:
        fpx = None
        fpy = None
        if feature['name'] == 'Great Red Spot':
            continue # dont' plot over the GRS - it's obvious on the map
        if planet.name == 'Mars':
            fpx = 360. - feature['longitude']
            fpy = feature['latitude']
        elif planet.name == 'Jupiter': 
            # Not sure if this is right... but there aren't any other features to test with
            do = feature['longitude'] - delta_longitude
            fpx = do if feature['longitude'] <= 180 else do - 360.
            fpy = feature['latitude']
        if fpx and fpy:
            ppx.append(fpx)
            ppy.append(fpy)
    ax.plot(ppx, ppy, 'yx')

    # Convert to a PNG image
    pngImage = io.BytesIO()
    FigureCanvas(fig).print_png(pngImage)
    # Encode PNG to Base64 string
    pngImageB64String = 'data:image/png;base64,'
    pngImageB64String += base64.b64encode(pngImage.getvalue()).decode('utf8')
    # close things
    plt.cla()
    plt.close(fig)
    return px, py, pngImageB64String
