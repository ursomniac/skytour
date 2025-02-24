from django.core.management.base import BaseCommand
from skytour.apps.dso.models import DSO, DSOObservingMode

class Command(BaseCommand):
    help = 'Create new TargetDSO for DSO --via [NBSMI][0-4][0-9] for mode/pri/viability'

    def add_arguments(self, parser):
        parser.add_argument('--test', action='store_true')
        parser.add_argument('--dso', dest='dso', type=int)
        parser.add_argument('--via', dest='viability', nargs='+', type=str, 
                help='Format: [NBSMI][0-4][0-9] for mode, priority, viability'
            )
    
    def handle(self, *args, **options):
        """
        Three ways this can run:
            - Create all new maps for all DSOs (all = True)
            - Create/Update maps for a subset of DSOs (dso_list=[ list of PKs ])
            - Create maps for DSOs that don't already have one (all=False, no dso_list)
        """
        via_opt = options['viability']
        via_raw = [] if not via_opt else via_opt

        viabilities = check_viabilities(via_raw)

        dso_pk = options['dso']
        dso = DSO.objects.filter(pk=dso_pk).first()
        
        if options['test']:
            print("VIA OPT: ", via_opt)
            print(f"DSO: {dso_pk} =  {dso}")
            vstr = ', '.join(via_raw)
            print(f"Viabilites: {vstr} = {viabilities}")
        else:
            if dso:
                run_dso(dso, viabilities, test=options['test'])
            else:
                print("DSO {dso_pk} not found - aborting")

def check_viabilities(raw):
    vialist = []
    for item in raw:
        if len(item) != 3:
            print(f"Wrong length for {item} - should be [NBSMI][0-4][0-9] - aborting")
        mode = item[0]
        if not (isinstance(mode, str) and mode.upper() in 'NBSMI'):
            print(f"Mode {mode} invalid - aborting")
            return None
        pri = int(item[1])
        if not(isinstance(pri, int) and pri >= 0 and pri <= 4):
            print(f"Priority {pri} invalid - aborting")
            return None
        via = int(item[2])
        if not(isinstance(via, int) and via >= 0):
            print(f"Viability {via} invalid - aborting")
            return None
        viatuple = (mode, pri, via)
        vialist.append(viatuple)
    print("VIALIST: ", vialist)
    return vialist

def run_dso(dso, viabilities, test=False):
    modes = dso.dsoobservingmode_set.all()
    for (mode, priority, viability) in viabilities:
        op = None
        vobj = modes.filter(mode=mode).first()
        if vobj is None:        # Create new mode
            vobj = DSOObservingMode()
            vobj.dso = dso
            op = 'Creating'
        else:                           # Existing mode - update
            op = 'Editing'
        vobj.mode = mode
        vobj.priority = priority
        vobj.viable = viability
        if not test:
            vobj.save()
        print(f"\t{op} Mode {mode} ({priority}, {viability})")
    return dso


