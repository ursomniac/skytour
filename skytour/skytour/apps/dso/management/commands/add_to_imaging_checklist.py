from django.core.management.base import BaseCommand
from ...helpers import create_atlas_plate
from ...models import DSO, DSOImagingChecklist


class Command(BaseCommand):
    help = 'Add DSO to Imaging Checklist'

    def add_arguments(self, parser):
        parser.add_argument('target', type=int)
        parser.add_argument('-p', '--priority', type=int, choices=[0, 1, 2, 3, 4, 5])
        parser.add_argument('-d', '--debug', dest='debug', action='store_true')
    
    def handle(self, *args, **options):
        debug = True if options['debug'] else False
        target = options['target']
        priority = options['priority'] if options['priority'] else None
        # For some reason using 0 turns it to None for NO REASON
        priority = 0 if priority is None else priority
        my_dso = DSO.objects.get(pk=target)
        if debug:
            print(f"DSO: {my_dso}")
            print(f"Priority: {priority}")

        if my_dso.dsoimagingchecklist_set.count() == 0:
            new = DSOImagingChecklist()
            new.dso = my_dso
            new.priority = priority
            new.save()
            print(f"DSO: {my_dso} added with priority = {priority}")
        else:
            c = my_dso.dsoimagingchecklist_set.first()
            if my_dso.priority != priority:
                c.priority = priority
                print(f"DSO: {my_dso} updated to priority = {priority}")
                c.save()
            else:
                print(f"DSO: {my_dso} already on imaging checklist")



