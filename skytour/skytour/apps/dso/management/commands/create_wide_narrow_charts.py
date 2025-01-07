import datetime, pytz
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from skyfield.api import load
from skytour.apps.dso.models import DSO
from skytour.apps.dso.finder import create_dso_finder_chart

class Command(BaseCommand):
    help = 'Create DSO wide/narrow finder charts'

    def add_arguments(self, parser):
        #parser.add_argument('--dso_list', dest='dso_list', nargs='+', type=int)
        parser.add_argument('--all', dest='all', action='store_true')
        parser.add_argument('--test', action='store_true')
        parser.add_argument('--wide', action='store_true', help='make wide chart only')
        parser.add_argument('--narrow', action='store_true', help='make narrow chart only')
        parser.add_argument('--nosave', action='store_true', help='do not update /media')
        parser.add_argument('--local', action='store_true', help='just save local copy')
        parser.add_argument('--start', nargs='?', const=0, type=int)
        parser.add_argument('--num', nargs='?', const=100 ,type=int)
        parser.add_argument('--dso_list', dest='dso_list', nargs='+', type=int)
    
    def handle(self, *args, **options):
        """
        Three ways this can run:
            - Create all new maps for all DSOs (all = True)
            - Create/Update maps for a subset of DSOs (dso_list=[ list of PKs ])
            - Create maps for DSOs that don't already have one (all=False, no dso_list)
        """
        all = options['all']
        start = options['start']
        num = options['num']
        save = not options['nosave']
        dso_opt = options['dso_list']
        save_local = options['local']
        dso_list = [] if not dso_opt else dso_opt

        both = options['wide'] == options['narrow']
        if not both:
            which = 'narrow' if options['narrow'] else 'wide'
        else:
            which = 'both'
        
        if options['test']:
            print("ALL: ", all)
            print("START: ", start)
            print("NUM: ", num)
            print("WHICH: ", which)
            print("DSO LIST: ", dso_list)
            print("SAVE: ", save)
        else:
            run_set(start=start, dso_list=dso_list, length=num, save=save, all=all, which=which, save_local=save_local)

MEDIA_PATH = 'media'

def run_dso(
        dso, 
        which='both', 
        save=True, 
        base_dir='', 
        save_local=False,
        t = None, ts=None, eph=None, earth=None
    ):

    if which in ['both', 'wide']:
        path = base_dir + 'dso_finder_wide/' if not save_local else ''
        finder_wide = create_dso_finder_chart(
            dso,
            utdt = None, 
            planets_dict = None, 
            asteroid_list = None,
            show_other_dsos = True,
            show_in_field_dsos = False,
            comet_list = None,
            now = False,
            save_file = save,
            chart_type = 'wide',
            path = path,
            include_mosaic = True,
            gear_list = ['eyepiece', 'equinox2', 'seestar50', 'seestar30'],
            ts = ts, t = t, eph = eph, earth=earth
        )
    else:
        finder_wide = None
        #print("skipped?")

    if which in ['both', 'narrow']:
        path = base_dir + 'dso_finder_narrow/' if not save_local else ''
        finder_narrow = create_dso_finder_chart(
            dso,
            utdt = None,
            fov = 2.5, # up to 2.5 for S30?
            mag_limit = 11.,
            show_other_dsos = True,
            show_in_field_dsos = True,
            now = False,
            planets_dict=None,
            asteroid_list=None,
            comet_list=None,
            save_file = save,
            chart_type = 'narrow',
            path = path,
            include_mosaic = False,
            gear_list = ['eyepiece', 'equinox2', 'seestar50', 'seestar30'],
            ts = ts, t = t, eph = eph, earth=earth
        )
    else:
        finder_narrow = None
        #print("skipped?")

    if save:
        if finder_narrow is not None:
            with open(f"/Users/robertdonahue/Temp/dso_finder_narrow/{finder_narrow}", 'rb') as f:
                data = f.read()
                f.close()
            dso.dso_finder_chart_narrow.save(f'{finder_narrow}', ContentFile(data))
        if finder_wide is not None:
            with open(f"/Users/robertdonahue/Temp/dso_finder_wide/{finder_wide}", 'rb') as f:
                data = f.read()
                f.close()
            dso.dso_finder_chart_wide.save(f'{finder_wide}', ContentFile(data))
    else:
        print("Not saving...")

    return finder_wide, finder_narrow, dso

def run_set(start=0, length=100, dso_list=[], save=True, all=False, which='both', save_local=False):
    dsos = DSO.objects.order_by('pk')

    ts = load.timescale() 
    t = ts.from_datetime(datetime.datetime.now(pytz.timezone('UTC'))) 
    eph = load('de421.bsp') 
    earth = eph['earth'] 

    if len(dso_list) == 0: 
        subset = dsos if all else dsos[start:(start+length)]
    else:
        subset = dsos.filter(pk__in=dso_list)

    total = subset.count()
    print(f"Running {total} DSOs")
    n = 0
    base_dir = '/Users/robertdonahue/Temp/' if not save_local else ''
    for dso in subset:
        n += 1
        print(f"Doing {n} of {total}:  PK #{dso.pk} = {dso}")
        fw, fn, new = run_dso(
            dso, 
            which=which, 
            save=save, 
            base_dir=base_dir, 
            save_local=save_local,
            ts=ts, t=t, eph=eph, earth=earth
        )
        print("\t... Done")
