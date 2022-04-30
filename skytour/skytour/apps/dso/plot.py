import base64
import datetime, pytz
from re import X
import io
from matplotlib import pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from scipy import spatial
from skyfield.api import load, Star
from skyfield.projections import build_stereographic_projection
from ..astro.angdist import chord_length
from ..astro.transform import get_cartesian
from ..dso.models import DSO
from ..plotting.map import *
from ..solar_system.plot import r2d, d2r
from ..utils.format import to_hm, to_dm
from .finder import plot_dso

def plate_list():
    ldec = [90, 75, 60, 45, 30, 15, 0, -15, -30, -45, -60, -75, -90]
    lsize = [1, 12, 16, 20, 24, 32, 48, 32, 24, 20, 16, 12, 1]
    mul = [0., 2.0, 1.5, 1.2, 1.0, 0.75, 0.5, 0.75, 1.0, 1.2, 1.5, 2.0, 0.]
    plate = {}
    j = 1
    for i in range(len(ldec)):
        dec = ldec[i]
        if abs(dec) == 90:
            plate[j] = (0, dec)
            j += 1
            continue
        ras = [x * mul[i] for x in range(lsize[i])]
        for ra in ras:
            plate[j] = (ra, dec)
            j += 1
    return plate

def get_fn(ra, dec, shapes=False):
    rah = int(ra)
    ram = int(60.*(ra - rah) + 0.00005)
    decs = 'N' if dec >= 0.0 else 'S'
    d = abs(dec)
    dd = int(d)
    dm = int(60.*(d - dd) + 0.00005)
    x = 'X' if shapes else ''
    return f"{rah:02d}{ram:02d}{decs}{dd:02d}{dm:02d}.png"

def get_dsos_on_plate(ra, dec, fov=20):
    fudge = 120
    dsos = DSO.objects.all()
    radius = chord_length(fov, degrees=True) * fudge
    coords = []
    for other in dsos:
        coords.append(other.get_xyz)
    center = get_cartesian(ra, dec, ra_dec=True)
    tree = spatial.KDTree(coords)
    neighbor_list = tree.query_ball_point([center], radius)
    neighbor_objects = []
    for idx in neighbor_list[[0][0]]:
        neighbor_objects.append(dsos[idx])
    return neighbor_objects

def create_atlas_plot(
        center_ra, center_dec, 
        reversed=False, mag_limit=9.5, 
        fov=20, save_file=True,
        mag_offset = 0, shapes = False,
        label_size = 'x-small',
        label_weight = 'normal',
    ):

    ts = load.timescale()
    # Datetime is arbitrary
    t = ts.from_datetime(datetime.datetime(2022, 1, 1, 0, 0).replace(tzinfo=pytz.utc)) # Arbitrary time
    eph = load('de421.bsp')
    earth = eph['earth']
    zenith = earth.at(t).observe(Star(ra_hours=center_ra, dec_degrees=center_dec))

    ra = to_hm(center_ra) # String value
    dec = to_dm(center_dec) # string value

    # Start up a Matplotlib plot
    style = 'dark_background' if reversed else 'default'
    plt.style.use(style)
    fig, ax = plt.subplots(figsize=[9,9])

    # center
    projection = build_stereographic_projection(zenith)
    angle = np.pi - fov / 360. * np.pi
    limit = np.sin(angle) / (1.0 - np.cos(angle))

    # NOW PLOT THINGS!
    # 1. stars and constellation lines
    ax, stars = map_hipparcos(ax, earth, t, mag_limit, projection, reversed=reversed, mag_offset=mag_offset)
    ax = map_constellation_lines(ax, stars, reversed=reversed)
    ax = map_bright_stars(ax, earth, t, projection, points=False, annotations=True, reversed=reversed)

    if shapes:    
        other_dso_records = DSO.objects.order_by('-major_axis_size')
        other_dsos = {'x': [], 'y': [], 'label': [], 'marker': []}
        for other in other_dso_records:
            x, y = projection(earth.at(t).observe(other.skyfield_object))
            if abs(x) > limit or abs(y) > limit:
                continue # not on the plot
            other_dsos['x'].append(x)
            other_dsos['y'].append(y)
            other_dsos['label'].append(other.shown_name)
            other_dsos['marker'].append(other.object_type.marker_type)
            ax = plot_dso(ax, x, y, other, alpha=0.6)
        xxx = np.array(other_dsos['x'])
        yyy = np.array(other_dsos['y'])
        for x, y, z in zip(xxx, yyy, other_dsos['label']):
            plt.annotate(
                z, (x, y), 
                textcoords='offset points',
                xytext=(5, 5),
                ha='left'
            )
    else:
        ax, _ = map_dsos(ax, earth, t, projection,
            center = (center_ra, center_dec), 
            reversed=reversed,
            label_size=label_size,
            label_weight=label_weight,
            product = 'atlas'
        )

    # Set the display
    ax.set_xlim(-limit, limit)
    ax.set_ylim(-limit, limit)
    ax.xaxis.set_visible(False)
    ax.yaxis.set_visible(False)
    secax = ax.secondary_xaxis('bottom', functions=(r2d, d2r))
    secax.set_xlabel('Degrees')
    secay = ax.secondary_yaxis('left', functions=(r2d, d2r))
    
    title = f"Chart: RA {ra}  DEC {dec}"
    ax.set_title(title)
    
    on_plate = get_dsos_on_plate(center_ra, center_dec, fov=fov)

    if save_file:
        fn = get_fn(center_ra, center_dec, shapes=shapes)
        fig.savefig('media/atlas_images/{}'.format(fn), bbox_inches='tight')
        plt.cla()
        plt.close(fig)
        return fn, on_plate

    plt.tight_layout(pad=2.0)
    # Convert to a PNG image
    pngImage = io.BytesIO()
    FigureCanvas(fig).print_png(pngImage)
    pngImageB64String = 'data:image/png;base64,'
    pngImageB64String += base64.b64encode(pngImage.getvalue()).decode('utf8')

    # close things
    plt.cla()
    plt.close(fig)
    return pngImageB64String, on_plate

"""
258 atlas plates
            1:     0, +90 N polar plot
      2 -  13:  2.0h, +75
     14 -  29:  1.5h, +60
     30 -  49:  1.2h, +45
     50 -  73:  1.0h, +30
     74 - 105: 0.75h, +15
    106 - 153:  0.5h,   0
    154 - 185: 0.75h, -15
    186 - 209:  1.0h, -30
    210 - 229:  1.2h, -45
    230 - 245:  1.5h, -60
    246 - 257:  2.0h, -75
          258:     0, -90 S polar plot
"""