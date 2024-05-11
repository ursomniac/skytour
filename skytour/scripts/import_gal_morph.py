from skytour.apps.dso.models import DSO, DSOInField
from skytour.apps.utils.models import ObjectType

def get_update_file():
    with open('data/Leda/gal_morph.tsv') as f:
        data = f.readlines()
    f.close()
    return data

def process_dsos(debug=True):
    data = get_update_file()
    otypes = get_object_types()
    for row in data:
        if "New Morph" in row:
            continue
        process_dso(row.strip(), otypes, debug=debug)

def process_dso(row, otypes, debug=True):
    fields = row.split('\t')
    id = fields[0]
    model = DSO if fields[0][0] == 'D' else DSOInField
    pk = int(fields[0][1:])
    name = fields[1]
    morph = fields[4]
    obj_type = fields[5]
    if obj_type not in otypes.keys():
        print(f"{id} {name}: MISSING Object Type {obj_type}")
        return
    if debug:
        #print(f"{id}: getting {name} from {model} PK = {pk}")
        pass
    obj = model.objects.get(pk=pk)
    obj.morphological_type = morph
    obj.object_type = otypes[obj_type]
    if debug:
        pass
    else:
        print(f"{id} {name}: Saving {morph} as {obj.object_type.slug}")
        obj.save()

def get_object_types():
    oo = ObjectType.objects.all()
    d = {
        'B': oo.filter(slug='galaxy--barred-spiral').first(),
        'C': oo.filter(slug='galaxy--cluster').first(),
        'D': oo.filter(slug='galaxy--dwarf').first(),
        'E': oo.filter(slug='galaxy--elliptical').first(),
        'I': oo.filter(slug='galaxy--intermediate').first(),
        'L': oo.filter(slug='galaxy--lenticular').first(),
        'S': oo.filter(slug='galaxy--spiral').first(),
        'X': oo.filter(slug='galaxy--irregular').first()
    }
    for k, v in d.items():
        if v is None:
            print(f"MISSING {k}")
    return d

if __name__ == '__main__':
    get_object_types()