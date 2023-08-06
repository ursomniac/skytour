from skytour.apps.dso.models import DSO, DSOImagingChecklist
import csv

def find_names(x):
    s = x.strip()
    if '=' in s:
        s = s[:s.index('=')].strip()

    if '+' in s:
        ss = s.split('+')
        ids = [z.strip() for z in ss]
    else:
        ids = [s]
    return ids

def find_dso(myid, n):
    #print("ID: ", myid, " TYPE: ", type(myid))
    try:
        cat, cid = myid.split(' ')
    except:
        print("Failed parsing: ", myid)
        return None
    if cat == 'NGC' and cid in ['3396', '3513', '4123']:
        return None # these are not in the DSO table
    if myid == 'Rho Oph':
        d = DSO.objects.get(id=213)
    else:
        d = DSO.objects.filter(catalog__abbreviation=cat, id_in_catalog=cid).first()
    
    if d is None:
        print(f"Row {n} ID: {myid} not found.")
    #else:
    #    print(f"Row {n} ID: {myid} found {d}")
    return d

def process_dso(dso, row, dryrun=True):
    translate = {'': 0, 'Low': 1, 'High': 2, 'HIGH': 3, 'HIGHEST': 4}
    priority = row[6].strip()
    # fix oopsies in file
    priority = 'HIGH' if priority == 'HGIH' else priority
    priority = 'HIGH' if priority == 'HIGH?' else priority
    priority = 'High' if priority == 'High?' else priority
    priority = 'HIGHEST' if priority == 'HGHEST' else priority
    priority = 'HIGHEST' if priority == 'HGIHEST' else priority
    priority = 'HIGH' if priority == 'Yes' else priority

    if dso.dec < -30.:
        issue = 'lowdec'
    elif priority == 'doable?':
        issue = 'questionable'
        priority = None
    elif dso.surface_brightness and dso.surface_brightness > 14.:
        issue = 'dim'
    elif dso.major_axis_size and dso.major_axis_size < 2.:
        issue = 'angsize'
    elif dso.magnitude and dso.magnitude >12.:
        issue = 'faint'
    else:
        issue = None

    if priority and priority not in translate.keys():
        print(f"Don't know what to do about {priority}")
        print("ROW: ", row)
        priority = ''
    pvalue = translate[priority] if priority else 0
    
    if not dryrun:
        obj = DSOImagingChecklist()
        obj.dso = dso
        obj.issues = issue
        obj.priority = pvalue
        obj.save()
        return obj
    return None

def run_things(dryrun=True):
    with open('skytour/test/eQuinox_DSO.csv') as f:
        reader = csv.reader(f)
        n = 0
        for row in reader:
            if n == 0:
                n += 1
                continue
            n += 1
            #print("TYPE: ", type(row[0]), "ROW: ", row[0])
            rawid = row[0]
            idlist = find_names(rawid)
            #print("IDLIST: ", idlist, ' TYPE: ', type(idlist))
            for lid in idlist:
                dso = find_dso(lid, n)
                if dso is None:
                    continue
                process_dso(dso, row, dryrun=dryrun)