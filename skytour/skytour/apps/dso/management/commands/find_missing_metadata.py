from django.core.management.base import BaseCommand
from ...models import DSO, DSOInField

class Command(BaseCommand):
    help = 'scrape Leda/Simbad for metadata and store'

    def add_arguments(self, parser):
        SOURCE_CHOICES = ['leda', 'simbad', 'any', 'both']
        MODEL_CHOICES = ['D', 'F']
        parser.add_argument('--source', nargs='?', default='leda', choices=SOURCE_CHOICES)
        parser.add_argument('--model', nargs='?', default='D', choices=MODEL_CHOICES)
        parser.add_argument('--debug', action='store_true')
        parser.add_argument('--verbose', action='store_true')

    def handle(self, *args, **options):
        verbose = options['verbose']
        debug = options['debug']
        source = options['source']
        code = options['model']

        if verbose:
            print("Source: ", source)
            print("Model: ", code)

        model = DSO if code == 'D' else DSOInField

        objects = model.objects.all()
        for obj in objects:
            has_leda = obj.metadata is not None and len(obj.metadata) > 4
            has_simbad = obj.simbad is not None and len(obj.simbad) > 4
            has_any = has_leda or has_simbad
            has_both = has_leda and has_simbad

            if source == 'leda' and not has_leda:
                print(f"{obj.pk} {obj.shown_name} missing Leda")
            elif source == 'simbad' and not has_simbad:
                print(f"{obj.pk} {obj.shown_name} missing Simbad")
            elif source == 'both' and not has_both:
                print(f"{obj.pk} {obj.shown_name} Leda = {has_leda} Simbad = {has_simbad} ")
            elif source == 'any' and not has_any:
                print(f"{obj.pk} {obj.shown_name} has no metadata")
            else:
                if verbose:
                    print(f"{obj.shown_name}: Leda = {has_leda} Simbad = {has_simbad}")

