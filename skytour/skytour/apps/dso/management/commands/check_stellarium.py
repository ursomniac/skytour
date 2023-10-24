
from django.core.management.base import BaseCommand
from ...models import DSO, DSOAlias
from ...helpers import create_atlas_plate
from skytour.apps.solar_system.utils import get_constellation

#  1 - (int)    - deep-sky object identificator
#  2 - (float)  - RA (decimal degrees)
#  3 - (float)  - Dec (decimal degrees)
#  4 - (float)  - B magnitude
#  5 - (float)  - V magnitude
#  6 - (string) - Object type (G, GX, GC, OC, NB, PN, DN, RN, C+N, HA, HII, SNR, BN, EN, SA, SC, RG, CL, IG, QSO or empty)
#  7 - (string) - Morphological type of object
#  8 - (float)  - Major axis size or radius (arcmin)
#  9 - (float)  - Minor axis size (arcmin)
# 10 - (int)    - Orientation angle (degrees)
# 11 - (float)  - Redshift
# 12 - (float)  - Error of redshift
# 13 - (float)  - Parallax (mas)
# 14 - (float)  - Error of parallax (mas)
# 15 - (float)  - Non-redshift distance (kpc)
# 16 - (float)  - Error of non-redsift distance (kpc)
# Cross-index columns:
# 17 - (int)    - NGC number (New General Catalogue)
# 18 - (int)    - IC number (Index Catalogue)
# 19 - (int)    - M number (Messier Catalog)
# 20 - (int)    - C number (Caldwell Catalogue)
# 21 - (int)    - B number (Barnard Catalogue)
# 22 - (int)    - Sh2 number (Sharpless Catalogue)
# 23 - (int)    - VdB number (Van den Bergh Catalogue of reflection nebulae)
# 24 - (int)    - RCW number (A catalogue of Hα-emission regions in the southern Milky Way)
# 25 - (int)    - LDN number (Lynds' Catalogue of Dark Nebulae)
# 26 - (int)    - LBN number (Lynds' Catalogue of Bright Nebulae)
# 27 - (int)    - Cr number (Collinder Catalogue)
# 28 - (int)    - Mel number (Melotte Catalogue of Deep Sky Objects)
# 29 - (int)    - PGC number (HYPERLEDA. I. Catalog of galaxies)
# 30 - (int)    - UGC number (The Uppsala General Catalogue of Galaxies)
# 31 - (string) - Ced number (Cederblad Catalog of bright diffuse Galactic nebulae)
# 32 - (int)    - Arp number (Atlas of Peculiar Galaxies)
# 33 - (int)    - VV number (The catalogue of interacting galaxies by Vorontsov-Velyaminov)
# 34 - (string) - PK identificator (Catalogue of Galactic Planetary Nebulae)
# 35 - (string) - PN G identificator (Strasbourg-ESO Catalogue of Galactic Planetary Nebulae)
# 36 - (string) - SNR G identificator (A catalogue of Galactic supernova remnants)
# 37 - (string) - ACO number (Rich Clusters of Galaxies by Abell et. al.)
# 38 - (string) - HCG identificator (Hickson Compact Group by Hickson P.)
# 39 - (string) - ESO identificator (ESO/Uppsala survey of the ESO(B) atlas by Lauberts)
# 40 - (string) - VdBH identificator (Van den Bergh and Herbst; Catalogue of southern stars embedded in nebulosity)
# 41 - (int)    - DWB number (Catalogue and distances of optically visible H II regions)
# 42 - (int)    - Tr number (Trumpler Catalogue)
# 43 - (int)    - St number (Stock Catalogue)
# 44 - (int)    - Ru number (Ruprecht Catalogue)
# 45 - (int)    - VdB-Ha number (van den Bergh-Hagen Catalogue)

CATS_WE_USE = {
    'M': 'messier', 'C': 'caldwell', 'NGC': 'ngc', 'IC': 'ic',
    'B': 'barnard', 'Cr': 'collinder', 'Mel': 'melotte', 'Tr': 'trumpler',
    'Sh2': 'sh2'
}
CATS = [
    # ones we use
    ('M', 19), ('C', 20), ('NGC', 17), ('IC', 18), 
    ('B', 21), ('Sh2', 22), ('Cr', 27), ('Mel', 28), ('Tr', 42),
    # ones we don't use
    ('PGC', 29), ('UGC', 30), ('Arp', 32), 
    ('VDB', 23), ('RCW', 24), ('LDN', 25), ('LBN', 26),
    ('Ced', 31),
    ('VV', 33), ('PK', 34), ('PN G', 35), ('SNR G', 36),
    ('ACO', 37), ('HCG', 38), ('ESO', 39), ('VdbH', 40),
    ('DWB', 41), ('St', 43), ('Ru', 44), ('Vdb-Ha', 45)
]

def get_dms(x, dms=False):
    if dms:
        my_sign = '+' if x >= 0. else '-'
    else:
        my_sign = ''
    y = abs(x)
    yh = int(y)
    y -= yh
    y *= 60.
    ym = int(y)
    y -= ym
    ys = y * 60.
    if dms:
        return f"{my_sign}{yh:02d}° {ym:02d}\' {ys:06.3f}\""
    else:
        return f"{yh:02d}h {ym:02d}m {ys:06.3f}s"

def get_primary_catalog(fields):
    for c in CATS: # tuple
        this_cat = c[0]
        this_id = fields[c[1]]
        if this_id and this_id != '0' and this_id != '':
            return this_cat, this_id
    print("Got Nothing for ", fields[1])
    return None, None
        
def lookup_dso(dsos, cat, id_in_cat):
        if cat in CATS_WE_USE.keys():
            found = dsos.filter(catalog__slug=CATS_WE_USE[cat], id_in_catalog=id_in_cat).first()
            # What about aliases?
            if found:
                return found, 'primary'
            if not found:
                x = DSOAlias.objects.filter(catalog__slug=CATS_WE_USE[cat], id_in_catalog=id_in_cat).first()
                if x:
                    return x.object, 'alias'
        return None, None

class Command(BaseCommand):
    help = 'Create DSO finder charts'

    def add_arguments(self, parser):
        # parser.add_argument('plates', nargs="*", type=int)
        # parser.add_argument('-s', '--shapes', dest='shapes', action='store_true')
        # parser.add_argument('-r', '--reversed', dest='reversed', action='store_true')
        # parser.add_argument('-a', '--all', dest='do_all', action='store_true')
        # parser.add_argument('-d', '--debug', dest='debug', action='store_true')
        # parser.add_argument('-f', '--full_set', dest='full_set', action='store_true')
        pass

    def handle(self, *args, **options):
        dsos = DSO.objects.all()
        new_dso = []
        old_dso = []
        issues_dso = []
        # debug = True if options['debug'] else False
        # data_file = '../../../../../stellarium_catalog.txt'
        data_file = 'stellarium_catalog.txt'
        
        with open(data_file) as f:
            while line := f.readline():
                line = line.rstrip()
                if line[0] == '#':
                    continue
                fields = line.split('\t')
                fields.insert(0, '') # so cols are 1-indexed

                # Filter by V or B
                vmag = None if fields[5] == '99' else float(fields[5])
                bmag = None if fields[4] == '99' else float(fields[4])
                use_mag = vmag if vmag else bmag

                # Filter by size
                maj_size = float(fields[8])
                min_size = float(fields[9])
                angle = float(fields[10])

                # Other metadata we want
                obj_type = fields[6]
                morph = fields[7]
                ra = float(fields[2]) / 15.
                dec = float(fields[3])

                cat, id_in_cat = get_primary_catalog(fields)
                # As near as I can tell, when there's no catalog, there's nothing on the map
                if cat is None and id_in_cat is None:
                    continue

                this_dso, how_found = lookup_dso(dsos, cat, id_in_cat)
                if this_dso:
                    old_dso.append(f"{this_dso}\t{how_found}")
                    continue

                issues = []
                if cat is None or id_in_cat is None:
                    issues.append(f"no ID")
                if maj_size == 0. and min_size == 0.:
                    issues.append(f"No size")
                if maj_size < 0.5:
                    issues.append(f"Too small: {maj_size}")
                if use_mag is None: 
                    issues.append(f"No mag")
                elif use_mag >= 13.0:
                    issues.append(f"Too Faint: {use_mag}")
                if cat not in CATS_WE_USE.keys(): 
                    issues.append(f"Cat {cat} not in use...")

                out = [
                    str(fields[1]), # id
                    str(cat), str(id_in_cat), # ID
                    str(obj_type), str(morph),
                    get_dms(ra), get_dms(dec, dms=True),
                    get_constellation(ra, dec)['abbr'].upper(),
                    str(vmag),
                    str(maj_size), str(min_size), str(angle),
                    ', '.join(issues)
                ]
                out_str = '\t'.join(out)
                if len(issues) > 0:
                    issues_dso.append(out_str)
                else:
                    new_dso.append(out_str)

                if int(fields[1]) % 10000 == 0:
                    print(f"Up to {fields[1]}")

        print(f"Found {len(old_dso)} existing DSOs")
        print(f"Found {len(new_dso)} new DSOs")
        print(f"Found {len(issues_dso)} DSOs with issues")
        with open('STEL_NEW.txt', 'w') as fnew:
            for new in new_dso:
                fnew.write(f"{new}\n")
        with open('STEL_OLD.txt', 'w') as fold:
            for old in old_dso:
                fold.write(f"{old}\n")
        with open('STEL_ISSUES.txt', 'w') as fissues:
            for iss in issues_dso:
                fissues.write(f"{iss}\n")
                
                    

                




