from django.core.management.base import BaseCommand
from ...wiki import update_dso_wiki
from ...models import DSO, DSOInField

class Command(BaseCommand):
    help = 'look up Wikipedia page for objects'

    def add_arguments(self, parser):
        SOURCE_CHOICES = ['leda', 'simbad']
        MODEL_CHOICES = ['D', 'F']
        parser.add_argument('--model', nargs='?', default='D', choices=MODEL_CHOICES)
        parser.add_argument('--dso_list', dest ='dso_list', nargs='*', type=int)
        parser.add_argument('--debug', action='store_true')
        parser.add_argument('--verbose', action='store_true')

    def handle(self, *args, **options):
        verbose = options['verbose']
        debug = options['debug']
        code = options['model']
        if verbose:
            print("Options: ",f"\tDebug: ", debug)
            print(f"\tModel: ", options['model'], f"\tDSO List: ", options['dso_list'])
        mymodel = DSO if code == 'D' else DSOInField
        if options['dso_list'] and len(options['dso_list']) > 0:
            objlist = mymodel.objects.filter(pk__in=options['dso_list'])
            for obj in objlist:
                update_dso_wiki(obj, debug=debug)

            