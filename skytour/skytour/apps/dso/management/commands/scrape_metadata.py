from django.core.management.base import BaseCommand
from ...metadata import process_object, get_metadata_from_source
from ...models import DSO, DSOInField

def get_obj_list(model, source):
    objlist = []
    allobj = model.objects.order_by('shown_name')
    for obj in allobj:
        if source == 'leda':
            if obj.metadata is None or obj.metadata['ra_float'] is None:
                objlist.append(obj)
        elif source == 'simbad':
            if obj.simbad is None or obj.simbad['ra_float'] is None:
                objlist.append(obj)
    return objlist

class Command(BaseCommand):
    help = 'scrape Leda/Simbad for metadata and store'

    def add_arguments(self, parser):
        SOURCE_CHOICES = ['leda', 'simbad']
        MODEL_CHOICES = ['D', 'F']
        parser.add_argument('--source', nargs='?', default='leda', choices=SOURCE_CHOICES)
        parser.add_argument('--model', nargs='?', default='D', choices=MODEL_CHOICES)
        parser.add_argument('--dso_list', dest ='dso_list', nargs='*', type=int)
        parser.add_argument('--find', action='store_true')
        parser.add_argument('--debug', action='store_true')
        parser.add_argument('--verbose', action='store_true')

    def handle(self, *args, **options):
        verbose = options['verbose']
        debug = options['debug']
        source = options['source']
        code = options['model']
        if verbose:
            print("Options: ",f"\tDebug: ", debug, f"\tSource: ", source)
            print(f"\tModel: ", options['model'], f"\tFind: ", options['find'], f"\tDSO List: ", options['dso_list'])
        mymodel = DSO if code == 'D' else DSOInField
        if options['dso_list'] and len(options['dso_list']) > 0:
            objlist = mymodel.objects.filter(pk__in=options['dso_list'])
        else:
            objlist = get_obj_list(mymodel, source)

        for obj in objlist:
            process_object(obj, code, source, debug=debug, verbose=verbose)

        