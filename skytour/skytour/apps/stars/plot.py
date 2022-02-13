import base64
import io
import numpy as np

from matplotlib import pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from skyfield.api import load, Star
from skyfield.projections import build_stereographic_projection

from ..observe.time import get_t_epoch, get_julian_date, get_last
from ..plotting.map import *
from ..site_parameter.helpers import find_site_parameter
from ..solar_system.moon import get_moon
from ..solar_system.helpers import get_all_planets
from ..solar_system.sun import  get_sun

def get_skymap(
        utdt, 
        location, 
        asteroid_list=None, 
        include_comets=True
    ):
    """
    Create a full map of the sky for a given UTDT and location.
    """ 
    # Parameters that might be in the SiteParameter apps/models
    priority = find_site_parameter('skymap-dso-priority', default=1, param_type='positive')
    star_mag_limit = find_site_parameter('skymap-magnitude-limit-stars', default=5.5, param_type='float')
    # TODO: should this be set from the limiting magnitude at the location based on its Bortle value?
    dso_mag_limit = find_site_parameter('skymap-magnitude-limit-dsos', default=6.0, param_type='float')
    
    # Set up SkyField
    ts = load.timescale()
    t = ts.from_datetime(utdt)
    eph = load('de421.bsp')
    earth = eph['earth']
    t0 = get_t_epoch(get_julian_date(utdt))
    last = get_last(utdt, location.longitude)

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
    fig, ax = plt.subplots(figsize=[10,10])

    # center
    projection = build_stereographic_projection(zenith)

    # NOW PLOT THINGS!

    # 1. stars and constellation lines
    ax, stars = map_hipparcos(ax, earth, t, star_mag_limit, projection)
    ax = map_constellation_lines(ax, stars)
    ax = map_bright_stars(
        ax, earth, t, projection, mag_limit=3.0, points=False, annotations=True
    )

    # 2. Sun - only matters if the plot is during the day
    sun = get_sun(utdt, eph=eph) 
    ax = map_single_object(ax, 'Sun', sun, earth, t, projection, color='red')

    # 3. Moon
    moon = get_moon(utdt, sun=sun, eph=eph)
    ax = map_single_object(ax, 'Moon', moon, earth, t, projection, color='red')
   
    # 4. Planets
    planets = get_all_planets(utdt, location=location)
    ax, interesting['planets'] = map_planets(ax, None, planets, earth, t, projection, center=(center_ra, center_dec))

    # 5. DSOs
    ax, interesting['dsos'] = map_dsos(ax, earth, t, projection, 
        center = (center_ra, center_dec),
        mag_limit=dso_mag_limit, 
        alpha=0.7, 
        priority=priority,
        color='grey'
    )

    # 6. Active Meteor Showers
    ax, interesting['meteor_showers'] = map_meteor_showers(ax, utdt, earth, t, projection, center=(center_ra, center_dec), size=250, color='#ffaa00')

    # 7. Asteroids
    if asteroid_list:
        ax, interesting['asteroids'] = map_asteroids(ax, asteroid_list, utdt, projection, center=(center_ra, center_dec))

    # 8. Comets
    if include_comets:
        ax, interesting['comets'] = map_comets(ax, utdt, earth, t, projection, center=(center_ra, center_dec))
        
    # 9. Put a circle for the horizon.
    horizon = plt.Circle((0,0), 1., color='b', fill=False)
    ax.add_patch(horizon)

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
    ax.set_title("{}".format(utdt.strftime("%Y-%m-%d %Hh UT")))

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
    
    return pngImageB64String, interesting, last