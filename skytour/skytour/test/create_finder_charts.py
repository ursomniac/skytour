from django.core.files.base import ContentFile
from skytour.apps.dso.models import DSO
from skytour.apps.dso.finder import create_dso_finder_chart

MEDIA_PATH = 'media'

def run_dso(dso, save=True):
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

    if save:
        with open(f"/Users/robertdonahue/Temp/dso_narrow/{finder_narrow}", 'rb') as f:
            data = f.read()
            f.close()
        dso.dso_finder_chart_narrow.save(f'{finder_narrow}', ContentFile(data))
        with open(f"/Users/robertdonahue/Temp/dso_wide/{finder_wide}", 'rb') as f:
            data = f.read()
            f.close()
        dso.dso_finder_chart_wide.save(f'{finder_wide}', ContentFile(data))

    return finder_wide, finder_narrow, dso

def run_all(start=0):
    dsos = DSO.objects.all()
    total = dsos.count()
    n = 0
    for dso in dsos:
        n += 1
        if n < start:
            continue
        print(f"Doing {n} of {total}: {dso}")
        fw, fn, new = run_dso(dso, save=True)
        print("\t... Done")
