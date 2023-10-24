
from django.core.management.base import BaseCommand
from ...models import DSO, DSOInField


class Command(BaseCommand):
    help = 'Dump DSO lists'

    def handle(self, *args, **options):
        data_file = 'DSO_DUMP.txt'
        dsos = DSO.objects.all()[:20]
        #with open(data_file, 'w') as f:
        for dso in dsos:
            print(f"{dso.shown_name}\t{dso.catalog.slug}\t{dso.id_in_catalog}")

           
                    

                



