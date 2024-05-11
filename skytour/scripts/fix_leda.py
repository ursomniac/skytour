from skytour.apps.dso.scrape.leda import process_leda_metadata
from skytour.apps.dso.models import DSO, DSOInField

def run_dsos(objs):
    for d in objs:
        if d.metadata is None:
            continue
        md = d.metadata
        if 'raw_values' in md.keys():
            continue
        if 'values' not in md.keys():
            continue
        if md['values'] is None:
            continue
        
        d.metadata['raw_values'] = d.metadata['values']
        d.metadata['values'] = process_leda_metadata(md['raw_values'])
        d.save()

def run_all():
    dd = DSO.objects.all()
    run_dsos(dd)
    ff = DSOInField.objects.all()
    run_dsos(ff)
