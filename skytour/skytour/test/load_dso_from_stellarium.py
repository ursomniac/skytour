from ..apps.dso.models import DSO

def get_new_fields(debug=True):
    """
    Add major/minor axis data.
    Add orientation angle.
    """
    dsos = DSO.objects.all()
    n_found = 0
    n_total = dsos.count()

    with open('stellarium_catalog.txt') as f:
        lines = f.readlines()
    for line in lines:
        if line[0] == '#':
            continue # skip comment lines

        fields = line.split('\t')
        #oangle = fields[9]
        #amajor = fields[7]
        #aminor = fields[8]
        dso_type = fields[5]
        morph = fields[6].strip()

        # OK - this gets a little tricky
        #   Find the DSO record for this record
        clist = [
            ('NGC', fields[16]),
            ('IC', fields[17]),
            ('M', fields[18]),
            ('C', fields[19]),
            ('B', fields[20]),
            ('Cr', fields[26])
        ]
        if fields[16] == '0' and fields[17] == '0' and fields[18] == '0' and fields[19] == '0' and fields[20] == '0' and fields[26] == '0':
            continue # no point in going further
        
        print (f"Testing {fields[0]}: V = {fields[4]} B = {fields[3]}, Type: {dso_type}, {morph}")
        found = False
        for (cat, id) in clist:
            dso = dsos.filter(catalog__abbreviation=cat, id_in_catalog=str(id)).first()
            if not dso is None: # found it!
                found = True
                break
        if not found: # went through the whole list
            print (f'\t did not find {clist}')
            continue
        # OK we have our DSO!
        n_found += 1
        #if oangle != 0 and amajor != 0 and aminor != 0:
        #    dso.orientation_angle = int(oangle) if int(oangle) >= 0 else None
        #    dso.major_axis_size = float(amajor)
        #    dso.minor_axis_size = float(aminor)
        #    print(f"FOUND: {dso.shown_name} = {amajor}\' x {aminor}\'  at {oangle}°")
        if len(morph) != 0:
            dso.morphological_type = morph
            if not debug:
                dso.save()
    p = 100. * n_found / float(n_total)
    print (f"Found {n_found} out of {n_total} DSDs = {p:.1f}%")
    
def find_dso(cat, id):
    with open('stellarium_catalog.txt') as f:
        lines = f.readlines()
    found = False
    for line in lines:
        if line[0] == '#':
            continue
        fields = line.split('\t')
        if cat == 'NGC':
            x = fields[16]
        elif cat == 'IC':
            x = fields[17]
        elif cat == 'B':
            x = fields[20]

        if id == x:
            found = True
            break
    if found:
        print (f"{cat} {id}: {fields[9]}°  {fields[7]}' x {fields[8]}'")
    else:
        print (f"Did not find {cat} {id}")
        