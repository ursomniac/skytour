from skytour.apps.dso.models import DSO, DSOObservingMode

def run_dso(dso, debug=True):
    modes = dso.targetdso.targetobservingmode_set.all()
    for mode in modes:
        print("\t{m}")

        if debug:
            print(f"\t\tmode = {mode.mode}")
            print(f"\t\tviable = {mode.viable}")
            print(f"\t\tpriority = {mode.priority}")
            print(f"\t\tinteresting = {mode.interesting}")
            print(f"\t\tchallenging = {mode.challenging}")
            print(f"\t\tnotes = {mode.notes}")
        else:
            # steps
            # 1. create new DSOObservingMode
            new = DSOObservingMode()
            # 2. set dso to dso
            new.dso = dso
            # 3. copy over fields
            new.mode = mode.mode                #   mode (char)
            new.viable = mode.viable            #   viable (psint)
            new.priority = mode.priority        #   priority (psint)
            new.interesting = mode.interesting  #   interesting (bool)
            new.challenging = mode.challenging  #   challenging (bool)
            new.notes = mode.notes              #   notes (text)
            new.save()
            print(f"\tCreated Modes for DSO {dso}")
            #except:
            #    print (f"\t\tFAILED to create mode {mode} for dso {dso}")


def run_all():
    dsos = DSO.objects.filter(pk__lt=10)
    for dso in dsos:
        t = dso.targetdso
        modes = t.targetobservingmode_set.all()
        print(f"{dso.pk:5d}: DSO {dso} has {modes.count()} modes [{t.mode_set}")
        run_dso(dso, debug=False)

