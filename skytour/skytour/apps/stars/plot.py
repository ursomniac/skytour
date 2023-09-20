import base64
import datetime
import io
import numpy as np
import time

from matplotlib import pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from skyfield.api import load, Star
from skyfield.projections import build_stereographic_projection

from ..astro.time import get_t_epoch, get_julian_date, get_last
from ..plotting.map import *
from ..site_parameter.helpers import find_site_parameter
from ..solar_system.plot import r2d, d2r
from ..utils.format import to_hm, to_dm

def get_skymap(
        utdt_start, 
        location, 
        planets=None,
        dso_list=None,
        asteroid_list=None, 
        comet_list=None,
        moon = None,
        sun = None,
        reversed=True,
        milky_way=False,
        simple=False,
        sky_limit = 70.,
        slew_limit=None,
        local_time = None,
        title = None,
        hours = 0.
    ):
    """
    Create a full map of the sky for a given UTDT and location.
    """ 
    utdt = utdt_start + datetime.timedelta(hours=hours)
    # Track performance
    times = [(time.perf_counter(), 'Start')]

    # Parameters that might be in the SiteParameter apps/models
    star_mag_limit = find_site_parameter('skymap-magnitude-limit-stars', default=5.5, param_type='float')
    star_mag_limit = 4.8 if simple else star_mag_limit
    # TODO: should this be set from the limiting magnitude at the location based on its Bortle value?
    
    # Set up SkyField
    ts = load.timescale()
    t = ts.from_datetime(utdt)
    eph = load('de421.bsp')
    earth = eph['earth']
    t0 = get_t_epoch(get_julian_date(utdt))
    last = get_last(utdt, location.longitude)
    times.append((time.perf_counter(), 'Initialize Ephem'))

    # This is the dict of "interesting" things on the map (planets, comets, etc.)
    interesting = {}

    # At a given UTDT/latitude, the zenith point x, y is:
    #   x = the local sidereal time
    #   y = the location latitude
    # which is the center of the plot.
    # So observe a fake Star() object at those coordinates.
    center_ra = last
    center_dec = location.latitude
    zenith = earth.at(t).observe(Star(ra_hours=center_ra, dec_degrees=center_dec))

    # Start up a Matplotlib plot
    style = 'dark_background' if reversed else 'default'
    plt.style.use(style)
    fig, ax = plt.subplots(figsize=[10,10])

    # center
    projection = build_stereographic_projection(zenith)
    times.append((time.perf_counter(), 'Starting Plot'))

    # NOW PLOT THINGS!

    # 1a Equator and Ecliptic
    ax = map_equ(ax, earth, t, projection, type='equ', reversed=reversed)
    ax = map_equ(ax, earth, t, projection, type='ecl', reversed=reversed)

    times.append((time.perf_counter(), 'Lines'))
    if milky_way:
        ax = map_milky_way(ax, earth, t, projection, line_width=2., colors=['#099', '#099'])
        if not simple:
            ax = map_equ(ax, earth, t, projection, type='gal', reversed=reversed)
        times.append((time.perf_counter(), 'Milky Way'))
    
    if not simple:
        ax = map_special_points(ax, earth, t, projection, colors=['#0cc', '#099'])
    
    # 1. stars and constellation lines
    ax, stars = map_hipparcos(ax, earth, t, star_mag_limit, projection, mag_offset=0.1, reversed=reversed)
    ax = map_constellation_lines(ax, stars, reversed=reversed)
    ax = map_bright_stars(
        ax, earth, t, projection, mag_limit=3.0, points=False, annotations=True, reversed=reversed
    )
    times.append((time.perf_counter(), 'Stars and Constellations'))
    # 1a. Constellation labels
    if simple:
        ax = map_constellation_labels(ax, earth, t, projection)

    # 2. Sun - only matters if the plot is during the day
    ax = map_single_object(ax, 'Sun', sun, earth, t, projection, color='red')
    times.append((time.perf_counter(), 'Sun'))

    # 3. Moon
    ax = map_single_object(ax, 'Moon', moon, earth, t, projection, color='red')
    times.append((time.perf_counter(), 'Moon'))

    # 4. Planets
    ax, interesting['planets'] = map_planets(ax, None, planets, earth, t, projection, center=(center_ra, center_dec))
    times.append((time.perf_counter(), 'Planets'))

    # 5. DSOs
    ax, interesting['dsos'] = map_dsos(ax, earth, t, projection, 
        center = (center_ra, center_dec),
        label_size='xx-small',
        reversed=reversed,
        dso_list=dso_list,
        ignore_setting = True,
        product = 'skymap'
    )
    times.append((time.perf_counter(), 'DSOs'))

    # 6. Active Meteor Showers
    if not simple:
        ax, interesting['meteor_showers'] = map_meteor_showers(
            ax, utdt, earth, t, projection, 
            center=(center_ra, center_dec), size=250, color='#ffaa00'
        )
        times.append((time.perf_counter(), 'Meteor Showers'))

    # 7. Asteroids
    if asteroid_list:
        ax, interesting['asteroids'] = map_asteroids(
            ax, None, asteroid_list, earth, t, projection, center=(center_ra, center_dec), reversed=reversed
        )
    times.append((time.perf_counter(), 'Asteroids'))

    # 8. Comets
    if comet_list:
        ax, interesting['comets'] = map_comets(
            ax, comet_list, earth, t, projection, center=(center_ra, center_dec), reversed=reversed
        )
    times.append((time.perf_counter(), 'Comets'))
        
    # 9. Put a circle for the horizon.
    horizon = plt.Circle((0,0), 1., color='b', fill=False)
    ax.add_patch(horizon)
    if not simple:
        sky_limit = plt.Circle((0,0), 70/90., color='#660', fill=False, ls='--')
        ax.add_patch(sky_limit)
    # Slew limit
    if slew_limit and not simple:
        slew_limit_circle = plt.Circle((0,0), (90.-slew_limit)/90., color='#660', fill=False, ls='--')
        ax.add_patch(slew_limit_circle)
    
    # Set the display
    fov = 180.
    angle = np.pi - fov / 360. * np.pi
    limit = np.sin(angle) / (1.0 - np.cos(angle))
    ax.set_xlim(-limit, limit)
    ax.set_ylim(-limit, limit)
    ax.xaxis.set_visible(False)
    ax.yaxis.set_visible(False)
    plt.tight_layout(pad=2.0)

    # Set title
    if title is None:
        title = utdt.strftime("%Y-%m-%d %Hh %Mm UT")
    if local_time is not None:
        title += f" = {local_time}"
    ax.set_title(title)
    times.append((time.perf_counter(), 'Plotting Complete'))

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
    times.append((time.perf_counter(), 'Rendering Complete'))

    return pngImageB64String, interesting, last, times

def get_zenith_map(
        utdt, 
        location, 
        mag_limit, 
        zenith_dist, 
        reversed=False,
        mag_offset = 0.5,
        center_ra = None,
        center_dec = None
    ):
    # Center is LAST, latitude
    ts = load.timescale()
    t = ts.from_datetime(utdt)
    eph = load('de421.bsp')
    earth = eph['earth']
    t0 = get_t_epoch(get_julian_date(utdt))
    last = get_last(utdt, location.longitude)
    if center_ra is None:
        center_ra = last
    if center_dec is None:
        center_dec = location.latitude
    zenith = earth.at(t).observe(Star(ra_hours=center_ra, dec_degrees=center_dec))

    ra = to_hm(center_ra) # String value
    dec = to_dm(center_dec) # string value

    # Start up a Matplotlib plot
    style = 'dark_background' if reversed else 'default'
    plt.style.use(style)
    fig, ax = plt.subplots(figsize=[9,9])

    # center
    projection = build_stereographic_projection(zenith)

    # NOW PLOT THINGS!
    # 1. stars and constellation lines
    ax, stars = map_hipparcos(
        ax, 
        earth, 
        t, 
        mag_limit, 
        projection, 
        mag_offset=mag_offset, 
        reversed=reversed
    )
    ax = map_constellation_lines(ax, stars, reversed=reversed)
    ax = map_bright_stars(
        ax, earth, t, projection, mag_limit=3.0, points=False, annotations=True, reversed=reversed
    )
    bright_stars = (stars.magnitude <= mag_limit)
    magnitude = stars['magnitude'][bright_stars]
    xx = stars['x'][bright_stars]
    yy = stars['y'][bright_stars]
    label_color = '#CC6' if reversed else '#66F'
    for x, y, z in zip(xx, yy, magnitude):
        ax.annotate(
            z, xy=(x, y),
            textcoords='offset points',
            xytext=(4, 4),
            horizontalalignment='left',
            annotation_clip=True,
            fontsize='x-small',
            color=label_color
        )

    # Put a circle for the horizon.
    r = math.radians(zenith_dist)/4.
    horizon = plt.Circle((0,0), r, color='b', fill=False)
    ax.add_patch(horizon)
    
    # Set the display
    fov = zenith_dist
    angle = np.pi - fov / 360. * np.pi
    limit = np.sin(angle) / (1.0 - np.cos(angle))
    ax.set_xlim(-limit, limit)
    ax.set_ylim(-limit, limit)
    ax.xaxis.set_visible(False)
    ax.yaxis.set_visible(False)
    secax = ax.secondary_xaxis('bottom', functions=(r2d, d2r))
    secax.set_xlabel('Degrees')
    secay = ax.secondary_yaxis('left', functions=(r2d, d2r))
    
    title = f"Zenith Chart: RA {ra}  DEC {dec}"
    ax.set_title(title)
    
    plt.tight_layout(pad=2.0)
    # Convert to a PNG image
    pngImage = io.BytesIO()
    FigureCanvas(fig).print_png(pngImage)
    pngImageB64String = 'data:image/png;base64,'
    pngImageB64String += base64.b64encode(pngImage.getvalue()).decode('utf8')

    # close things
    plt.tight_layout()
    plt.cla()
    plt.close(fig)
    return pngImageB64String, last