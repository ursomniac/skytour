from django.core.files.base import ContentFile
from skytour.apps.dso.models import DSO
from skytour.apps.dso.finder import create_dso_finder_chart

MEDIA_PATH = 'media'

def run_dso(dso, which='both', save=True):
    if which in ['both', 'wide']:
        finder_wide = create_dso_finder_chart(
            dso,
            utdt = None, 
            planets_dict = None, 
            asteroid_list = None,
            comet_list = None,
            now = False,
            save_file = save,
            path = '/Users/robertdonahue/Temp/dso_wide'
        )
    else:
        finder_wide = None

    if which in ['both', 'narrow']:
        finder_narrow = create_dso_finder_chart(
            dso,
            utdt = None,
            fov = 2.,
            mag_limit = 11.,
            show_other_dsos = False,
            now = False,
            planets_dict=None,
            asteroid_list=None,
            comet_list=None,
            save_file = save,
            path = '/Users/robertdonahue/Temp/dso_narrow'
        )
    else:
        finder_narrow = None

    if save:
        if finder_narrow is not None:
            with open(f"/Users/robertdonahue/Temp/dso_narrow/{finder_narrow}", 'rb') as f:
                data = f.read()
                f.close()
            dso.dso_finder_chart_narrow.save(f'{finder_narrow}', ContentFile(data))
        if finder_wide is not None:
            with open(f"/Users/robertdonahue/Temp/dso_wide/{finder_wide}", 'rb') as f:
                data = f.read()
                f.close()
            dso.dso_finder_chart_wide.save(f'{finder_wide}', ContentFile(data))

    return finder_wide, finder_narrow, dso

def run_set(start=0, length=100, all=False, which='both'):
    dsos = DSO.objects.order_by('pk')
    subset = dsos if all else dsos[start:start+length]
    total = subset.count()
    n = 0
    for dso in subset:
        n += 1
        if n < start:
            continue
        print(f"Doing PK {n} of {total}: {dso}")
        fw, fn, new = run_dso(dso, save=True)
        print("\t... Done")
