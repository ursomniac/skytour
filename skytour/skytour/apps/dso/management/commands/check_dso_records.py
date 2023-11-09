from django.core.management.base import BaseCommand
from ...models import DSO

class Command(BaseCommand):
    help = 'Check DSO records'
    
    def handle(self, *args, **options):
        all = DSO.objects.all()
        for dso in all:

            # test 1 - check for finder image
            try:
                chart = dso.dso_imaging_chart.url
                if chart is None or len(chart) == 0:
                    print(f"{dso.pk}: {dso} missing imaging chart")
            except:
                print(f"{dso.pk}: {dso} Error with imaging chart test")
            # test 2 imaging priority
            #check = dso.dsoimagingchecklist_set.count()
            #if dso.dec < -35 and check > 0:
            #    print(f"{dso.pk}: {dso} has imaging priority with Dec < -35")
            #elif dso.dec >= -35 and check == 0:
            #    print(f"{dso.pk}: {dso} has no imaging priority with dec >= -35")
