import math
from .models import AtlasPlate
from .plot import plate_list

def get_sep(ra1, dec1, ra2, dec2):
    dra = ra1 - ra2
    dt1 = math.sin(dec1) * math.sin(dec2)
    dt2 = math.cos(dec1) * math.cos(dec2) * math.cos(dra)
    cos_d = dt1 + dt2
    sep = math.degrees(math.acos(cos_d))
    return sep

def get_position_angle(ra1, dec1, ra2, dec2):
    dra = ra1 - ra2
    pa1 = math.sin(dra)
    pa2 = math.cos(dec2) * math.tan(dec1)
    pa3 = math.sin(dec2) * math.cos(dra)
    pa = math.degrees(math.atan2(pa1, pa2-pa3))
    return pa

def get_relative_positions(p1, p2):
    plates = plate_list()
    pp1 = plates[p1]
    pp2 = plates[p2]
    p1_dec = math.radians(pp1[1])
    p1_ra = math.radians(pp1[0] * 15.)
    p2_dec = math.radians(pp2[1])
    p2_ra = math.radians(pp1[0] * 15.)
    
    # angular separation
    sep = get_sep(p1_ra, p1_dec, p2_ra, p2_dec)

    # position angle
    if abs(pp1[1]) == 90:
        pa = 0.
    else:
        pa = get_position_angle(p1_ra, p1_dec, p2_ra, p2_dec)
    return sep, pa

def sign(x):
    if x < 0:
        return -1.
    if x > 0:
        return 1.
    return 0

def find_neighbors(my_ra, my_dec, limit=20.):
    plate_dict = plate_list()
    plate_keys = plate_dict.keys()
    my_ra = math.radians(my_ra * 15.)
    my_dec = math.radians(my_dec)

    neighbors = []
    nstr = []
    for plate in plate_keys:
        #if plate == p:
        #    continue
        ra = math.radians(plate_dict[plate][0] * 15.)
        dec = math.radians(plate_dict[plate][1])
        sep = get_sep(my_ra, my_dec, ra, dec)
        pa = get_position_angle(my_ra, my_dec, ra, dec)
        # Create an index based on the sep and pa
        xdist = sep * sign(pa)
        if sep < limit:
            pobj = AtlasPlate.objects.get(plate_id=plate)
            p = dict(
                plate=plate,
                obj = pobj,
                sep = sep,
                pa = pa,
                ra = pobj.center_ra,
                dec = pobj.center_dec,
                xdist = xdist
            )
            neighbors.append(p)
    return neighbors

def assemble_neighbors(plist):
    rows = []
    plates_in_row = []
    row_dec = None
    # trick is sorted()
    # newlist = sorted(list_to_sort, key=lambda: d['pa'])
    for p in plist:
        dec = p['obj'].center_dec
        if row_dec is None:
            row_dec = dec
        if dec != row_dec: # start new row
            if len(plates_in_row) > 0:
                z = sorted(plates_in_row, key=lambda d: d['xdist'])
                rows.append(z) # use sorted here
                plates_in_row = []
                row_dec = dec
        plates_in_row.append(p)
    if len(plates_in_row) > 0:
        z = sorted(plates_in_row, key=lambda d: d['xdist'])
        rows.append(z) # use sorted here
    return rows

def test_neighbor(p1, p2):
    plate_dict = plate_list()
    pp1 = plate_dict[p1]
    pp2 = plate_dict[p2]
    p1_ra = math.radians(pp1[0] * 15)
    p1_dec = math.radians(pp1[1])
    p2_ra = math.radians(pp2[0] * 15.)
    p2_dec = math.radians(pp2[1])
    sep = get_sep(p1_ra, p1_dec, p2_ra, p2_dec)
    print (f"{pp1} to {pp2} = {sep}")