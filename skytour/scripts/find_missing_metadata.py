from skytour.apps.dso.models import DSO, DSOInField

def getid(d):
    model = 'D' if d._meta.model_name == 'dso' else 'F'
    return f"{model}{d.pk:05d}"

def run_dsos(dsos, out=[]):
    for d in dsos:
        if d.metadata is None and d.simbad is None:
            id = getid(d)
            line = f"{id}\t{d.shown_name}\t{d.hyperleda_name}\t{d.simbad_name}\n"
            out.append(line)
    return out

def run_all():
    out = []
    out = run_dsos(DSO.objects.all(), out)
    out = run_dsos(DSOInField.objects.all(), out)
    with open('missing_metadata.txt', 'w') as f:
        for row in out:
            f.write(row)
    f.close()