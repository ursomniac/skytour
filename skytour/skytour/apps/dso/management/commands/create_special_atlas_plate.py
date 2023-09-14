from django.core.management.base import BaseCommand
from ...helpers import create_special_atlas_plate
from ...models import AtlasPlateSpecial


class Command(BaseCommand):
    help = 'Create Special Atlas Plate'

    def add_arguments(self, parser):
        parser.add_argument('plates', nargs="*", type=int)
        parser.add_argument('-s', '--shapes', dest='shapes', action='store_true')
        parser.add_argument('-r', '--reversed', dest='reversed', action='store_true')
        parser.add_argument('-a', '--all', dest='do_all', action='store_true')
        parser.add_argument('-d', '--debug', dest='debug', action='store_true')
        parser.add_argument('-f', '--full_set', dest='full_set', action='store_true')
    
    def handle(self, *args, **options):
        debug = True if options['debug'] else False
        reversed = True if options['reversed'] else False
        shapes = True if options['shapes'] else False
        do_all = True if options['do_all'] else False
        full_set = True if options['full_set'] else False
        #plates = range(1,259) if do_all else options['plates']
        plates = options['plates']

        if debug:
            print (f"Reversed: {reversed} Shapes: {shapes} Do all: {do_all}")
            print(f"Plate List: {plates}")

        for plate_id in plates: 
            instance = AtlasPlateSpecial.objects.filter(plate_id=plate_id).first()
            if instance:
                if not full_set:
                    print("Plate: ", plate_id, " Shapes: ", shapes, " Reversed: ", reversed)
                    fn = create_special_atlas_plate(plate_id, shapes=shapes, reversed=reversed)
                else:
                    for rev in [True, False]:
                        for shape in [True, False]:
                            print("Plate: ", plate_id, " Shapes: ", shape, " Reversed: ", rev)
                            fn = create_special_atlas_plate(plate_id, shapes=shape, reversed=rev)
            else:
                print(f"Plate ID {plate_id} invalid.")