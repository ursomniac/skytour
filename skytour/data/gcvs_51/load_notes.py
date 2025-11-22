import re
from skytour.apps.stars.models import VariableStar, VariableStarNotes

def get_id_text(line):
    c = re.sub(r"\s+"," ",line)
    words = c.split(' ')
    name = ' '.join(words[:2])
    rest = ' '.join(words[2:]) + '\n'
    return name, rest

def get_object(id):
    obj = VariableStar.objects.filter(name=id).first()
    return obj

def process_file():
    with open('data/gcvs_51/gcvs_remark.txt') as f:
        lines = f.readlines() # keep newlines!
    d = {}
    for line in lines:
        id, text = get_id_text(line)
        if id not in d.keys():
            d[id] = ''
        else:
            d[id] += text
    return d

def process_objects(d):
    for k, v in d.items():
        obj = get_object(k)
        if k is None:
            print("ERROR with {k}")
            continue
        nobj, created = VariableStarNotes.objects.get_or_create(gcvs=obj)
        nobj.notes = v
        nobj.save()