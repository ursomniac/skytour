from django.core.management.base import BaseCommand
from ...models import DSO

class Command(BaseCommand):
    help = 'Check for missing DSO images'
    
    def handle(self, *args, **options):
        all = DSO.objects.all()
        for dso in all:
            if dso.images.count() == 0:   
                s = dso.shown_name
                a = dso.alias_list
                if a is not None and len(a) > 0:
                    s = s + ', ' + a             
                print(s)