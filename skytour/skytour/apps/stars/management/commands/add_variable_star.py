from django.core.management.base import BaseCommand
from ...aavso import *
from ...models import ObservableVariableStar, VariableStar

class Command(BaseCommand):
    help = 'Create DSO wide/narrow finder charts'

    def add_arguments(self, parser):
        parser.add_argument('--mag_limit', type=float, default=14.5, help='chart magnitude limit')
        parser.add_argument('--fov', type=float, default=60.0, help='chart fov in arcmin')
        parser.add_argument('--name', type=str, help='put in quotes')
        parser.add_argument('--debug', action='store_true')
        parser.add_argument('--test', action='store_true', help='Do not create object, just report')
        # TODO: lines, boundaries, labels

    def handle(self, *args, **options):
        debug = options['debug']
        fov = options['fov']
        mag_limit = options['mag_limit']
        test = options['test']
        name = options['name']   
             
        if debug:
            print(f"Name: {name}")
            print(f"FOV: {fov:.1f}°")
            print(f"Mag. Limit: {mag_limit:.1f}")
            print(f"Test: {test}")

        parent = VariableStar.objects.filter(name=name).first()
        if parent is None:
            id = construct_id(name)
            if id is not None and len(id) >= 6:
                parent = VariableStar.objects.filter(id_in_catalog=id).first()

            if parent is None:
                print(f"ERROR: Star name {name} and ID {id} not found - ABORTING")
                exit(1)
        if parent and debug:
            print(parent)
        
        d = process_star(name, maglimit=mag_limit, fov=fov, debug=debug)
        
        if not test:
            obs, created = ObservableVariableStar.objects.get_or_create(gcvs=parent)
            obs.finder_chart = d['image_path']
            obs.finder_chart_mag = mag_limit
            obs.finder_chart_fov = fov
            obs.finder_json = d['json']
            obs.save()
