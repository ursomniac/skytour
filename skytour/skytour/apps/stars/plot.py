import base64
import io
import numpy as np

from matplotlib import pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from skyfield.api import load, Star
from skyfield.projections import build_stereographic_projection

from ..observe.time import get_t_epoch, get_julian_date, get_last
from ..plotting.map import *
from ..solar_system.moon import get_moon
from ..solar_system.planets import get_all_planets
from ..solar_system.sun import  get_sun

def get_skymap(utdt, location, mag_limit=6, priority=2, asteroid_list=None):
    """
    Create a full map of the sky for a given UTDT and location.
    """ 
    ts = load.timescale()
    t = ts.from_datetime(utdt)
    eph = load('de421.bsp')
    earth = eph['earth']
    t0 = get_t_epoch(get_julian_date(utdt))
    last = get_last(utdt, location.longitude)

    # At a given UTDT/latitude, the zenith point x, y is:
    #   x = the local sidereal time
    #   y = the location latitude
    zenith = earth.at(t).observe(Star(ra_hours=last, dec_degrees=location.latitude))

    # Start the plot
    fig, ax = plt.subplots(figsize=[12,12])

    # center
    projection = build_stereographic_projection(zenith)

    # stars and constellation lines
    ax, stars = map_hipparcos(ax, earth, t, 5.5, projection)
    ax = map_constellation_lines(ax, stars)
    ax = map_bright_stars(
        ax, earth, t, projection, mag_limit=3.0, points=False, annotations=True
    )
    # Sun - only matters if the plot is during the day
    sun = get_sun(utdt, eph=eph) 
    ax = map_single_object(ax, 'Sun', sun, earth, t, projection, color='red')
    # Moon
    moon = get_moon(utdt, sun=sun, eph=eph)
    ax = map_single_object(ax, 'Moon', moon, earth, t, projection, color='red')
   
    # planets
    planets = get_all_planets(utdt, location=location)
    ax = map_planets(ax, None, planets, earth, t, projection)

    # DSOs
    # Only show highest and high priority objects (2)
    # Limiting magnitude of 6.
    ax = map_dsos(ax, earth, t, projection, 
        mag_limit=mag_limit, 
        alpha=0.7, 
        priority=priority,
        color='grey'
    )
    # Meteor Showers if active
    ax = map_meteor_showers(ax, utdt, earth, t, projection, size=250, color='#ffaa00')

    # Asteroids
    if asteroid_list:
        ax = map_asteroids(ax, asteroid_list, utdt, projection)

    # Put a circle for the horizon.
    horizon = plt.Circle((0,0), 1., color='b', fill=False)
    ax.add_patch(horizon)

    fov = 180.
    angle = np.pi - fov / 360. * np.pi
    limit = np.sin(angle) / (1.0 - np.cos(angle))
    ax.set_xlim(-limit, limit)
    ax.set_ylim(-limit, limit)
    ax.xaxis.set_visible(False)
    ax.yaxis.set_visible(False)

    # set title
    ax.set_title("{}".format(utdt.strftime("%Y-%m-%d %Hh UT")))

    # Render and close
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