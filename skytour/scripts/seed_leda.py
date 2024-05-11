import json
from skytour.apps.dso.models import DSO

def find_content(fn):
    try:
        with open(fn) as f:
            data = json.load(f)
        f.close()
        return data
    except:
        return None

def handle_object(obj, model):
    fn = f"data/Leda/obj_{model}{obj.pk:05d}.json"
    content = find_content(fn)
    if content is not None:
        obj.metadata = content
        obj.save()

def process_dso(dso):
    handle_object(dso, 'D')
    field_objects = dso.dsoinfield_set.all()
    for field in field_objects:
        handle_object(field, 'F')

def process_dsos():
    dsos = DSO.objects.all()
    for dso in dsos:
        print("Processing ", dso)
        process_dso(dso)