import base64
import datetime, pytz
from re import X
import io
from django.db.models import Q
from matplotlib import pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from scipy import spatial
from skyfield.api import load, Star
from skyfield.projections import build_stereographic_projection

from ..astro.angdist import chord_length
from ..astro.transform import get_cartesian
from ..dso.models import DSO
from ..plotting.map import *
from ..utils.format import to_hm, to_dm
from ..utils.models import ConstellationBoundaries, ConstellationVertex

from .finder import plot_dso
from .models import AtlasPlate
from .vocabs import MILKY_WAY_CONTOUR_COLORS

# These are used to create a secondary axis on the plot.
def r2d(a): # a is a numpy.array
    return a * (180.*2) / math.pi # Why times 2?  I have no idea, but it's the only way it works...
def d2r(a): # a us a numpy.array
    return a * math.pi / (180.*2)



def get_fn(ra, dec, plate_id, shapes=False, reversed=reversed):
    """
    Create a filename for an AtlasPlate instances based on the properties of the plate
    (if shapes or markers are used and whether is printable = black on white, or reversed = white on black).
    """
    rah = int(ra)
    ram = int(60.*(ra - rah) + 0.00005)
    decs = 'N' if dec >= 0.0 else 'S'
    d = abs(dec)
    dd = int(d)
    dm = int(60.*(d - dd) + 0.00005)
    xx = []
    if shapes:
        xx.append('shapes')
    if reversed:
        xx.append('reversed')
    aux = '-'.join(xx)
    if len(aux) > 0:
        aux = '-' + aux
    return f"{plate_id:03d}-{rah:02d}{ram:02d}{decs}{dd:02d}{dm:02d}{aux}.png"

def get_dsos_on_plate(ra, dec, fov=20):
    """
    Get all of the DSOs shown on a plate based on the ra/dec of the plate center.
    This isn't 100% perfect, some things RIGHT on the edge might not appear.
    It's also possible that it might include DSOs that are JUST off the edge.
    But mostly it works.
    """
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

def get_boundary_lines(plate_id):
    """
    Get all of the constellation boundaries seen on a plate.
    This is slightly optimized: it uses the list of known constellations on the plate,
    and only returns the lines relevant to them.   
    """
    plate = AtlasPlate.objects.get(plate_id=plate_id)
    # get constellations on plate
    const_list = plate.constellation.all()
    # get vertices for these constellations
    verts = ConstellationVertex.objects.filter(constellation__in=const_list)
    vert_list = verts.values_list('pk', flat=True)
    # get boundary line segments
    segments = ConstellationBoundaries.objects.filter(Q(start_vertex__in=vert_list) | Q(end_vertex__in=vert_list))
    lines = {}
    p = 0
    for seg in segments:
        v1 = seg.start_vertex
        v2 = seg.end_vertex
        t = tuple([v1, v2])
        if t not in lines.keys():
            lines[t] = []
        lines[t].append(tuple([seg.ra, seg.dec]))
        p += 1
    return lines, p

def map_constellation_boundaries(ax, plate_id, earth, t, projection, reversed=False):
    """
    Map the constellation boundaries.
    """
    lines, _ = get_boundary_lines(plate_id)
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

def create_atlas_plot(
        center_ra, center_dec, plate_id,
        reversed=False, mag_limit=9.5, 
        fov=None, save_file=True,
        mag_offset = 0, shapes = False,
        label_size = 'x-small',
        label_weight = 'normal',
        model = AtlasPlate
    ):
    """
    Create an AtlasPlate image.
    TODO: Change annontation font weight to be BOLD for high/highest priority!
    """
    fov = fov if fov else 20.
    object = model.objects.get(plate_id=plate_id)
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
    # 1. stars constellation lines
    ax = map_plate_neighbors(ax, object, reversed=reversed)
    if model == AtlasPlate:
        ax = map_constellation_names(ax, object, earth, t, projection, reversed=reversed)

    ax = map_equ(ax, earth, t, projection, 'ecl', reversed=reversed)
    ax = map_equ(ax, earth, t, projection, 'gal', reversed=reversed)
    if abs(center_dec <= 15.):
        ax = map_equ(ax, earth, t, projection, 'equ', reversed=reversed)

    ax = map_milky_way(ax, earth, t, projection, reversed=reversed, colors=MILKY_WAY_CONTOUR_COLORS[1])
    ax = map_milky_way(ax, earth, t, projection, reversed=reversed, contour=2, colors=MILKY_WAY_CONTOUR_COLORS[2])
    ax = map_special_points(ax, earth, t, projection, reversed=reversed)
    if model == AtlasPlate:
        ax = map_constellation_boundaries(ax, plate_id, earth, t, projection, reversed=reversed)
    ax, stars = map_hipparcos(ax, earth, t, mag_limit, projection, reversed=reversed, mag_offset=mag_offset)
    line_color = '#99f' if reversed else "#00f4" # constellation-line
    ax = map_constellation_lines(ax, stars, reversed=reversed, line_color=line_color)
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
            ax = plot_dso(ax, x, y, other, 
                alpha=0.6, 
                reversed=reversed, 
                min_size=10.
            )
        xxx = np.array(other_dsos['x'])
        yyy = np.array(other_dsos['y'])
        text_color = '#6ff' if reversed else '#333' # annotation
        for x, y, z in zip(xxx, yyy, other_dsos['label']):
            plt.annotate(
                z, (x, y), 
                textcoords='offset points',
                xytext=(5, 5),
                ha='left',
                color = text_color,
                fontweight = label_weight,
                fontsize=label_size
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
    
    title = f"Plate: {plate_id} -  RA {ra}  DEC {dec}"
    ax.set_title(title)
    
    on_plate = get_dsos_on_plate(center_ra, center_dec, fov=fov)
    path = 'atlas_images' if model == AtlasPlate else 'atlas_images_special' 

    if save_file:
        fn = get_fn(center_ra, center_dec, plate_id, shapes=shapes, reversed=reversed)
        fig.savefig(f'media/{path}/{fn}', bbox_inches='tight')
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

4 special plates
    Com/Vir
    Fornax
    SMC
    LMC
"""

def create_atlas_legend():
    """
    TODO: write this.
    This creates an image showing all the lines/symbols on the atlas.
    TODO: put all the colors together in a single dictionary!
    """
    pass