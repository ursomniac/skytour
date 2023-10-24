from django.core.management.base import BaseCommand
from ...models import DSO
from ...finder import create_dso_finder_chart

class Command(BaseCommand):
    help = 'Create DSO finder charts'

    def add_arguments(self, parser):
        parser.add_argument('--dso_list', dest='dso_list', nargs='+', type=int)
        parser.add_argument('--all', dest='all', action='store_true')
        parser.add_argument('--test', action='store_true')
    
    def handle(self, *args, **options):
        """
        Three ways this can run:
            - Create all new maps for all DSOs (all = True)
            - Create/Update maps for a subset of DSOs (dso_list=[ list of PKs ])
            - Create maps for DSOs that don't already have one (all=False, no dso_list)
        """
        dso_list = None
        all = False
        just_new = False

        if options['all']:
            all = options['all']
            print ("ALL is true")
        elif options['dso_list']:
            dso_list = options['dso_list']
            print ("GOT DSOs: ", dso_list)
        else:
            just_new = True
            print ("Running new DSOs")

        if dso_list:
            dsos = DSO.objects.filter(pk__in=dso_list)
        else:
            dsos = DSO.objects.all()

        for dso in dsos:
            if just_new and dso.dso_finder_chart:
                continue
            
            # Otherwise operate!
            print("Creating/Updating Finder Chart for {}: {}".format(dso.pk, dso.label_on_chart))

            fn = create_dso_finder_chart(
                dso, 
                test=options['test'],
                show_in_field_dsos = False, 
                reversed=False, 
                save_file=True
            )
            if not options['test']:
                dso.dso_finder_chart = 'dso_charts/{}'.format(fn)
                #print ("\tFN: ", fn)
                dso.save()