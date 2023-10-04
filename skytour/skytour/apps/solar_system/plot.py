import base64
import datetime
import io
import math
import matplotlib
import numpy as np
import time
from matplotlib import pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from skyfield.api import load, Star
from skyfield.magnitudelib import planetary_magnitude
from skyfield.projections import build_stereographic_projection
from ..astro.time import get_t_epoch, get_julian_date
from ..plotting.map import *
from .asteroids import get_asteroid_target, fast_asteroid
from .comets import get_comet_target, get_comet_magnitude
from .utils import get_constellation
from .vocabs import ZODIAC


matplotlib.use('Agg') # this gets around the threading issues.

def r2d(a): # a is a numpy.array
    return a * (180.*2) / math.pi # Why times 2?  I have no idea, but it's the only way it works...
def d2r(a): # a us a numpy.array
    return a * math.pi / (180.*2)

def r2am(a):
    return 60. * a * 360. / math.pi
def am2r(a):
    return a * math.pi / 360. / 60.

def r2as(a):
    return a * 360. * 3600. / math.pi
def as2r(a):
    return a * math.pi / (360.*3600.)

def sizeme(mag, limit):
    return (0.5 + limit - mag) **2.0

def create_finder_chart(
        utdt,                   # UTDT
        instance,               # Planet instance
        planets_cookie,         # metadata from cookie
        asteroids,              # asteroids cookie
        object_type = 'planet', # override for Moon
        obj_cookie = None,      # override cookie for Moon
        fov = None,             # force FOV
        flipped = False,        # Flip E-W
        reversed = True,        # B on W or W on B
        mag_limit = 8.5,        # magnitude limit of stars
        mag_offset = 0.05,
        show_axes = False,      #
        sun = None,
        moon = None
    ):
    # Start timer
    times = [(time.perf_counter(), 'Start')]

    if object_type == 'moon':
        name = 'Moon'
        pdict = obj_cookie
    elif object_type == 'asteroid':
        name = instance.full_name
        pdict = obj_cookie
    elif object_type == 'comet':
        name = instance.name
        pdict = obj_cookie
    else: # I am a planet
        name = instance.name
        pdict = planets_cookie[name]
    
    ra = pdict['apparent']['equ']['ra']
    dec = pdict['apparent']['equ']['dec']

    ts = load.timescale()
    t = ts.from_datetime(utdt)
    eph = load('de421.bsp')
    earth = eph['earth']
    target = earth.at(t).observe(Star(ra_hours=ra, dec_degrees=dec))
    projection = build_stereographic_projection(target)
    times.append((time.perf_counter(), 'Astrometrics done'))

    # Start making a plot
    style = 'dark_background' if reversed else 'default'
    plt.style.use(style)
    
    fig, ax = plt.subplots(figsize=[6,6])
    times.append((time.perf_counter(), 'Map set up'))

    # Add equator and ecliptic
    ax = map_equ(ax, earth, t, projection, 'equ', reversed=reversed)
    ax = map_equ(ax, earth, t, projection, 'ecl', reversed=reversed)
    ax = map_equ(ax, earth, t, projection, 'gal', reversed=reversed)
    # Add stars from Hipparcos, constellation lines (from Stellarium),
    #   and Bayer/Flamsteed designations from the BSC
    ax, stars = map_hipparcos(ax, earth, t, mag_limit, projection, mag_offset=mag_offset, reversed=reversed)
    ax = map_constellation_lines(ax, stars, reversed=reversed)
    ax = map_bright_stars(ax, earth, t, projection, points=False, annotations=True, reversed=reversed)
    times.append((time.perf_counter(), 'Stars/Constellations'))

    # Don't plot the planet - just a symbol.
    ax = map_target(ax, ra, dec, projection, earth, t, '+')
    ax = map_eyepiece(ax, reversed=reversed)
    times.append((time.perf_counter(), 'Symbol/Eyepiece'))

    # Add planet symbols (Unicode)
    ax, _ = map_planets(ax, name, planets_cookie, earth, t, projection)
    times.append((time.perf_counter(), 'Other planets'))


    # 2. Sun - only matters if the plot is during the day
    if sun is not None:
        ax = map_single_object(ax, 'Sun', sun, earth, t, projection, color='red')
        times.append((time.perf_counter(), 'Sun'))

    # 3. Moon
    if moon is not None:
        ax = map_single_object(ax, 'Moon', moon, earth, t, projection, color='red')
        times.append((time.perf_counter(), 'Moon'))
        
    # Add DSOs
    ax, _ = map_dsos(ax, earth, t, projection, 
        reversed=reversed, product='finder'
    )
    times.append((time.perf_counter(), 'DSOs'))

    # Asteroids
    ax, _ = map_asteroids(ax, name, asteroids, earth, t, projection)
    times.append((time.perf_counter(), 'Asteroids'))

    # legend
    #kw = dict(prop="sizes", num=6, fmt="{x:.2f}",
    #    func=lambda s: -1.*(np.sqrt(s)-0.5-mag_limit) )
    #legend2 = ax.legend(*scatter.legend_elements(**kw), loc="upper left", title="Mag.")

    # Plot scaling
    if not fov: # set FOV if not supplied
        fov = 8. if name in ['Uranus', 'Neptune'] else 20.
    angle = np.pi - fov / 360.0 * np.pi
    limit = np.sin(angle) / (1.0 - np.cos(angle))

    if flipped:
        ax.set_xlim(limit, -limit)
    else:
        ax.set_xlim(-limit, limit)
    ax.set_ylim(-limit, limit)

    ax.xaxis.set_visible(show_axes)
    ax.yaxis.set_visible(show_axes)
    secax = ax.secondary_xaxis('bottom', functions=(r2d, d2r))
    secax.set_xlabel('Degrees')
    secay = ax.secondary_yaxis('left', functions=(r2d, d2r))

    flip_text = ' - (flipped)' if flipped else ''
    const = pdict['observe']['constellation']['abbr']
    title = f"{name} Finder Chart (in {const}) {flip_text}"
    ax.set_title(title)
    times.append((time.perf_counter(), 'Plotting...'))

    # Convert to a PNG image
    pngImage = io.BytesIO()
    FigureCanvas(fig).print_png(pngImage)
    pngImageB64String = 'data:image/png;base64,'
    pngImageB64String += base64.b64encode(pngImage.getvalue()).decode('utf8')

    # close things
    plt.tight_layout()
    plt.cla()
    plt.close(fig)
    times.append((time.perf_counter(), 'Rendering as PNG'))
    return pngImageB64String, times


def create_planet_system_view (
        utdt,                   # UTDT
        planet,                 # Planet instance
        cookie,                 # metadata from cookie
        object_type = 'planet', # Override for Moon
        fov = None,             # force FOV
        flipped = True,         # Flip X axis for eyepice view
        reversed = True,        # B on W or W on B
        min_sep = None, 
    ):
    # Start timer
    times = [(time.perf_counter(), 'Start')]

    if object_type == 'moon':
        pdict = cookie # Moon 
        name = 'Moon'
    else:        
        name = planet.name
        pdict = cookie[name]

    planet_ra = pdict['apparent']['equ']['ra']
    planet_dec = pdict['apparent']['equ']['dec']
    ang_size_radians = math.radians(pdict['observe']['angular_diameter'])
    ts = load.timescale()
    t = ts.from_datetime(utdt)
    t0 = get_t_epoch(get_julian_date(utdt))
    eph = load('de421.bsp')
    earth = eph['earth']
    target = earth.at(t).observe(Star(ra_hours=planet_ra, dec_degrees=planet_dec))
    projection = build_stereographic_projection(target)
    times.append((time.perf_counter(), 'Astrometrics done'))

    # Start making a plot
    style = 'dark_background' if reversed else 'default'
    plt.style.use(style)
    
    fig, ax = plt.subplots(figsize=[6,6])
    times.append((time.perf_counter(), 'Map set up'))

    # Add moons
    moons = pdict.get('moons', None)
    if moons:
        # return the maximum separation of a moon from its planet.
        # This determines the scale of the view.
        ax, moon_pos_list, max_sep = map_moons(ax, pdict, earth, t, projection, ang_size_radians, reversed=reversed)
        for x, y, z, o in zip(moon_pos_list['x'], moon_pos_list['y'], moon_pos_list['label'], moon_pos_list['o']):
            plt.annotate(z, (x, y), textcoords='offset points', xytext=(0, o), ha='center')
        ax.set_xlabel('ID above + = moon behind planet in orbit;\nID below + = moon in front of planet in orbit')
    else: # no moons, set max_sep to 3*ang_size of the planet.
        max_sep = 3 * ang_size_radians
    if min_sep and max_sep < min_sep:
        max_sep = min_sep

    # If Saturn, add rings
    # TODO: deal with having the ring in front of the planet and then behind it.
    if name == 'Saturn':
        ax = map_saturn_rings(ax, pdict, t0, reversed=reversed)

    # Moon and inferior planets have phases!
    if name in ['Moon', 'Mercury', 'Venus']:
        ax = map_phased_planet(ax, pdict, ang_size_radians)
    else: # just a regular disk for superior planets
        ax = map_whole_planet(ax, ang_size_radians, reversed=reversed)

    # Plot scaling
    # THIS IS WAY MORE COMPLICATED THAN IT OUGHT TO BE.
    if not fov: # set FOV if not supplied
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
    if flipped:
        ax.set_xlim(limit, -limit)
    else:
        ax.set_xlim(-limit, limit)
    ax.set_ylim(-limit, limit)

    ax.xaxis.set_visible(False)
    ax.yaxis.set_visible(False)

    if limit < 0.0003:
            secax = ax.secondary_xaxis('bottom', functions=(r2as, as2r))
            secax.set_xlabel('Arcsec')
            secay = ax.secondary_yaxis('left', functions=(r2as, as2r))
    else:
        secax = ax.secondary_xaxis('bottom', functions=(r2am, am2r))
        secax.set_xlabel('Arcminutes')
        secay = ax.secondary_yaxis('left', functions=(r2am, am2r))

    if object_type != 'moon':
        title = "{} Telescope View".format(name)
        if flipped:
            title += " (flipped)"
    else:
        title = "Lunar Disk View"

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

def plot_ecliptic_positions(planets, reversed):
    dmax = 48
    r = [0., ]
    theta = [0., ]
    label = ['Sun', ]
    colors = ['y', 'grey', 'orange', 'blue', 'red', 'pink', 'brown', 'lime', 'cyan']
    fig = plt.figure()
    ax = fig.add_subplot(projection='polar')
    style = 'dark_background' if reversed else 'default'
    sym_color = '#fff' if reversed else '#000'
    plt.style.use(style)
    
    for d in planets:
        r.append(d['distance'])
        theta.append(math.radians(d['longitude']))
        label.append(d['name'])

    #ax.set_xticks = (np.arange(0, 2.*math.pi, math.pi/12.))
    ax.set_xticks(np.arange(0, 2.*np.pi, np.pi/6.0))
    ax.set_ylim(0, dmax)
    ax.set_rscale('symlog')
    c = ax.scatter(theta, r, s=40, c=colors)

    for (_, longitude, symbol) in ZODIAC:
        plt.annotate(
            symbol, 
            (math.radians(longitude+30.), dmax*1.5),
            color = sym_color,
            weight='bold',
            size='large',
            textcoords='offset points', 
            xytext=(0, 0), 
            ha='center', 
            va='center',
            annotation_clip = False
        )

    # Convert to a PNG image
    pngImage = io.BytesIO()
    FigureCanvas(fig).print_png(pngImage)
    # Encode PNG to Base64 string
    pngImageB64String = 'data:image/png;base64,'
    pngImageB64String += base64.b64encode(pngImage.getvalue()).decode('utf8')
    # close things
    plt.cla()
    plt.close(fig)
    return pngImageB64String, planets

def plot_track(
        utdt, 
        object_type='planet', 
        object=None, 
        offset_before=-60, 
        offset_after=61, 
        step_days=5, 
        step_label=5,
        mag_limit=None, 
        dsos=False, 
        #planets=None,
        fov=None,
        reversed=True,
        return_data = True,
        debug=False
    ):
    """
    Planet is from the Planet model
    utdt is the MIDPOINT date.
    """
    ts = load.timescale()
    eph = load('de421.bsp')
    earth = eph['earth']
    sun = eph['sun']
    if object_type == 'planet':
        target = eph[object.target]
    elif object_type == 'asteroid':
        target = get_asteroid_target(object, ts, sun)
    elif object_type == 'comet':
        target, comet_row = get_comet_target(object, ts, sun)
        
    t = ts.from_datetime(utdt)

    first_projection = earth.at(t).observe(target)
    style = 'dark_background' if reversed else 'default'
    plt.style.use(style)

    fig, ax = plt.subplots(figsize=[8,8])
    projection = build_stereographic_projection(first_projection)
    # Build the observation points
    data = []
    d_planet = dict(x = [], y = [], label = [])
    i = 0
    min_x = 0
    max_x = 0
    min_y = 0
    max_y = 0
    first = True
    for dt in range(offset_before, offset_after, step_days):
        this_utdt = utdt + datetime.timedelta(days=dt)
        tt = ts.from_datetime(this_utdt)
        z = earth.at(tt).observe(target).apparent()
        ra, dec, distance = z.radec()
        
        earth_sun = earth.at(tt).observe(sun)
        r_earth_sun = earth_sun.radec()[2].au.item()

        sun_target = sun.at(tt).observe(target)
        r_sun_target = sun_target.radec()[2].au.item()

        mag = None
        if object_type == 'asteroid':
            mag = fast_asteroid(object, target, tt, earth, sun, r_earth_sun)
        elif object_type == 'planet':
            mag = planetary_magnitude(z).item()
        elif object_type == 'comet' and comet_row is not None:
            mag_g = comet_row['magnitude_g']
            mag_k = comet_row['magnitude_k']
            mag_offset = object.mag_offset if object is not None else 0.
            mag = get_comet_magnitude(mag_g, mag_k, distance.au.item(), r_sun_target, offset=mag_offset)

        if return_data:
            data.append(dict(
                utdt = this_utdt,
                ra = ra.hours.item(),
                dec = dec.degrees.item(),
                distance = distance.au.item(),
                constellation = get_constellation(ra.hours.item(), dec.degrees.item()),
                mag = mag
            ))

        if first:
            starting_position = z
            first = False

        xx, yy = projection(earth.at(tt).observe(Star(ra_hours=ra.hours, dec_degrees=dec.degrees)))
        min_x = xx if xx < min_x else min_x
        max_x = xx if xx > max_x else max_x
        min_y = yy if yy < min_y else min_y
        max_y = yy if yy > max_y else max_y

        d_planet['x'].append(xx)
        d_planet['y'].append(yy)
        lll = "{}/{:2d}".format(this_utdt.month, this_utdt.day) if i%step_label == 0 else ''
        d_planet['label'].append(lll)
        i += 1
    if debug:
        print (d_planet['label'])
    line_color = 'red' if reversed else 'orange'
    w = ax.plot(d_planet['x'], d_planet['y'], color=line_color, marker=None)
    plus_color = 'orange' if reversed else '#900'
    w = ax.scatter(d_planet['x'], d_planet['y'], s=90., c=plus_color, marker='+', alpha=0.7)

    label_color = 'goldenrod' if reversed else 'maroon'
    for x, y, l in zip(d_planet['x'], d_planet['y'], d_planet['label']):
        ax.annotate(
            l, xy=(x, y), 
            textcoords='offset points',
            xytext=(3, 10),
            horizontalalignment='left',
            color=label_color
        )
    
    ax = map_equ(ax, earth, t, projection, 'equ', reversed=reversed)
    ax = map_equ(ax, earth, t, projection, 'ecl', reversed=reversed)
    ax = map_equ(ax, earth, t, projection, 'gal', reversed=reversed)

    # Add stars from Hipparcos, constellation lines (from Stellarium),
    #   and Bayer/Flamsteed designations from the BSC
    if not mag_limit:
        if object_type == 'planet' and object.slug not in ['uranus', 'neptune']:
            mag_limit = 6.0
        elif object_type in ['comet', 'asteroid']:
            mag_limit = 10.
        else:
            mag_limit = 9.0

    print("MAG LIMIT: ", mag_limit)
    ax, stars = map_hipparcos(ax, earth, t, mag_limit, projection, reversed=reversed)
    ax = map_constellation_lines(ax, stars, reversed=reversed)
    ax = map_bright_stars(ax, earth, t, projection, points=False, annotations=True, mag_limit=mag_limit, reversed=reversed)
    
    # Add DSOs
    if dsos:
        ax, _ = map_dsos(ax, earth, t, projection, product='finder')

    # TODO: Add (other) planets
    # Would need multiple tracks...
    #if planets:
    #    ax, _ = map_planets(ax, None, planets_cookie, earth, t, projection)

    if fov:
        angle = np.pi - fov / 360.0 * np.pi
        limit = 2. * np.sin(angle) / (1.0 - np.cos(angle))
        avg_x = (min_x + max_x) / 2.
        avg_y = (min_y + max_y) / 2.
        ax.set_xlim(avg_x-limit, avg_x+limit)
        ax.set_ylim(avg_y-limit, avg_y+limit)
    else:
        dx = (max_x - min_x) * 0.25
        ax.set_xlim(min_x-dx, max_x+dx)
        ax.set_ylim(min_y-dx, max_y+dx)


    ax.xaxis.set_visible(False)
    ax.yaxis.set_visible(False)
    secax = ax.secondary_xaxis('bottom', functions=(r2d, d2r))
    secax.set_xlabel('Degrees')
    secay = ax.secondary_yaxis('left', functions=(r2d, d2r))

    title = "Track for {}".format(object.name)
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
    return pngImageB64String, starting_position, data

def get_planet_map(planet, physical):
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
        #print ("returning None")
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
        #print("Angle: ", angle)
        #print("∆L: ", delta_longitude)
        #print("DO: ", do)
        #print ("PX: ", px)
        py = d_e
    elif planet.name == 'Mars':
        im = ax.imshow(im, extent=[360, 0, -90, 90])
        px = angle + 360 if angle < 0 else angle
        py = d_e
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
