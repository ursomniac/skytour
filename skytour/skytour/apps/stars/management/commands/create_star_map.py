import datetime, pytz
import numpy as np

from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from matplotlib import pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib import patches
from skyfield.api import load, Star
from skyfield.projections import build_stereographic_projection
from skytour.apps.plotting.map import *

from skytour.apps.site_parameter.helpers import get_ephemeris
from skytour.apps.utils.format import to_sex

class Command(BaseCommand):
    help = 'Create DSO wide/narrow finder charts'

    def add_arguments(self, parser):
        parser.add_argument('--ra', type=float, default=0.0)
        parser.add_argument('--dec', type=float, default=0.0)
        parser.add_argument('--fov', type=float, default=20.)
        parser.add_argument('--mag_limit', type=float, default=6.0)
        parser.add_argument('--path', type=str, default="~/Desktop/")
        parser.add_argument('--output_file', type=str, default=None)
        parser.add_argument('--title', type=str, default='Skytour Starmap')
        parser.add_argument('--constellation_lines', action='store_true')
        parser.add_argument('--label_stars', action="store_true")
        parser.add_argument('--scale', type=float, default=1.0)
        parser.add_argument('--test', action='store_true')
        # TODO: lines, boundaries, labels
    
    def handle(self, *args, **options):
        ra = options['ra']
        dec = options['dec']
        fov = options['fov']
        mag_limit = options['mag_limit']
        path = options['path']
        if path[-1] != '/':
            path += '/'
        output_file = options['output_file']
        if output_file is None:
            rastr = to_sex(ra, format="fra")
            decstr = to_sex(dec, format='fdec')
            output_file = f"skytour-starmap-{rastr}{decstr}.png"
        constellation_lines = options['constellation_lines']
        label_stars = options['label_stars']
        scale = options['scale']
        title = options['title']
        test = options['test']
        axes = False
        
        if test:
            print(f"RA: {ra:.5f}")
            print(f"Dec.: {dec:.4f}")
            print(f"FOV: {fov:.1f}°")
            print(f"Mag. Limit: {mag_limit:.1f}")
            print(f"Path: {path}")
            print(f"Scale: {scale}")
            print(f"Output File: {output_file}")

        ts = load.timescale()
        t = ts.from_datetime(datetime.datetime.now(pytz.timezone('UTC'))) 
        eph = load(get_ephemeris()) 
        earth = eph['earth']

        # Center the chart on the DSO
        center = earth.at(t).observe(Star(ra_hours=ra, dec_degrees=dec))
        projection = build_stereographic_projection(center)
        field_of_view_degrees = fov

        # plot
        plt.style.use('default')
        fig, ax = plt.subplots(figsize=[8,8])
        angle = np.pi - field_of_view_degrees  / 360.0 * np.pi
        limit = np.sin(angle) / (1.0 - np.cos(angle))
        ax, stars = map_hipparcos(ax, earth, t, mag_limit, projection, star_scale=scale)
        if constellation_lines:
            ax = map_constellation_lines(ax, stars)
        if label_stars:    
            ax = map_bright_stars(ax, earth, t, projection, points=False, annotations=True, reversed=reversed)

        # scaling
        ax.set_xlim(-limit, limit)
        ax.set_ylim(-limit, limit)
        # axis labels
        if not axes:
            ax.xaxis.set_visible(False)
            ax.yaxis.set_visible(False)
        #secax = ax.secondary_xaxis('bottom', functions=(r2d, d2r))
        #secax.set_xlabel('Degrees')
        #secay = ax.secondary_yaxis('left', functions=(r2d, d2r))
        ax.set_aspect(1.0)
        ax.set_title(title)

        print(f"Saving to {path}{output_file}")
        try:
            fig.savefig('{}{}'.format(path, output_file), bbox_inches='tight')
            out = f"{path}{output_file}"
        except:
            out = './test_starmap.png'
            fig.savefig('./test_starmap.png', bbox_inches='tight')
        plt.cla()
        plt.close(fig)
        return out