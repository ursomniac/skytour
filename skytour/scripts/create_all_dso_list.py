from skytour.apps.dso.models import DSO

def get_name(obj):
    if obj.catalog.abbreviation == 'OTHER':
        return obj.id_in_catalog
    elif obj.catalog.abbreviation == 'C':
        aliases = obj.aliases.all()
        for c in ['NGC', 'IC', 'Tr', 'Cr', 'Mel']:
            test = aliases.filter(catalog__abbreviation=c).first()
            if test is not None:
                return f"{test.catalog.abbreviation} {test.id_in_catalog}"
        print("Can't fix {obj}")
    elif obj.catalog.abbreviation == 'B':
        return f"Barnard {obj.id_in_catalog}"    
    return f"{obj.catalog.abbreviation} {obj.id_in_catalog}"

def create_list():
    l = []
    dd = DSO.objects.all().order_by('pk')
    for d in dd:
        print("DOING ", d)
        name = get_name(d)
        if name[:3] == 'Ast':
            continue
        l.append(f"D{d.pk:05d}\t{name}\n")
        ff = d.dsoinfield_set.all()
        for f in ff:
            name = get_name(f)
            l.append(f"F{f.pk:05d}\t{name}\n")
    with open("dso_list.txt", 'w') as f:
        for dso in l:
            f.write(dso)
    f.close()
