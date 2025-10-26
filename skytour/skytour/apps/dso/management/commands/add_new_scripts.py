from django.core.management.base import BaseCommand
from ...models import DSO
from ...atlas_utils import find_neighbors

def process_steps(dso, options, debug=False):
    infield = dso.dsoinfield_set.all()
    nearby = list(filter(None, dso.nearby_dsos))
    nearby_pks = ' '.join([str(d.pk) for d in nearby])
    fpks = ' '.join([str(f.pk) for f in infield])

    if debug:
        print("Nearby PKs: ", nearby_pks)
        print("Field PKs: ", fpks)

    # step 1 - metadata
    for source in ['simbad', 'leda']:
        print(f"python manage.py scrape_metadata --source {source} --model D --dso_list {dso.pk}")
        if infield.count() > 0:
            print(f"python manage.py scrape_metadata --source {source} --model F --dso_list {fpks}")

    # step 2 - finder charts
    print (f"python manage.py create_wide_narrow_charts --dso_list {dso.pk}")
    print (f"python manage.py create_wide_narrow_charts --dso_list {nearby_pks}")
    print (f"python manage.py create_dso_finder_charts --dso_list {dso.pk}")
    print (f"python manage.py create_dso_finder_charts --dso_list {nearby_pks}")

    # step 3 - update atlas plates
    nn = find_neighbors(dso.ra_float, dso.dec_float)
    plate_pks = ' '.join([str(x['plate']) for x in nn])
    print (f"python manage.py create_atlas_plate -f {plate_pks} ")

    # step 4 - misc
    print(f"python manage.py create_dso_pdf --dso_list {dso.pk}")

class Command(BaseCommand):
    help = 'scrape Leda/Simbad for metadata and store'

    def add_arguments(self, parser):
        parser.add_argument('--dso', type=int)
        parser.add_argument('--debug', action='store_true')

    def handle(self, *args, **options):
        debug = options['debug']
        pk = options['dso']
        if debug:
            print("Options:")
            print(f"\tDebug: ", debug)
            print(f"\tDSO PK: ", pk)

        # 1. Get the DSO
        dso = DSO.objects.filter(pk=pk).first()
        if dso is None:
            print("Cannot find DSO - aborting")
        else:
            process_steps(dso, options, debug=debug)
        

        