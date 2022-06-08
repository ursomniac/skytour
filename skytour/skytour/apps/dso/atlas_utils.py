import math
from .models import AtlasPlate

def get_sep(ra1, dec1, ra2, dec2):
    """
    Return angular separation (degrees) between two coordinates.
    This will NOT WORK for small angular separations (cos d ---> 1 - tiny number).
    """
    dra = ra1 - ra2
    dt1 = math.sin(dec1) * math.sin(dec2)
    dt2 = math.cos(dec1) * math.cos(dec2) * math.cos(dra)
    cos_d = dt1 + dt2
    sep = math.degrees(math.acos(cos_d))
    return sep

def get_position_angle(ra1, dec1, ra2, dec2):
    """
    Return the position angle between two coordinates and North.

    We're using this to sort out the direction a neighboring plate is at.
    For plates centered at the poles (where PA is indeterminate), return
    the direction as it would appear on the plate (i.e., a clock-face direction).
    """
    if abs(dec1) < math.radians(90.):
        dra = ra1 - ra2
        pa1 = math.sin(dra)
        pa2 = math.cos(dec2) * math.tan(dec1) 
        pa3 = math.sin(dec2) * math.cos(dra)
        pa = math.degrees(math.atan2(pa1, pa2-pa3))
    else:
        pa = (270. - math.degrees(ra2)) % 360.
        
    return pa

def get_relative_positions(p1, p2):
    """
    Return the relative positions (sep, PA) between two AtlasPlate instances.
    """
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
    """
    Python doesn't have a sgn method...
    Return -1, 0, 1 based on a value (<0, 0, >0).
    """
    if x < 0:
        return -1.
    if x > 0:
        return 1.
    return 0

def find_neighbors(my_ra, my_dec, limit=20.):
    """
    Find all neighbors to an AtlasPlate instance, i.e., all plates that overlap.
    This fails for plates 1 and 258 because all the neighbors end up in the same place.
    That's because abs(dec) == 90 and so tan(dec) is ∞.
    """
    plate_dict = plate_list()
    plate_keys = plate_dict.keys()
    my_ra = math.radians(my_ra * 15.)
    my_dec = math.radians(my_dec)

    neighbors = []
    for plate in plate_keys:
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
    """
    Given a list of neighboring plates, assemble them into a 2-d list,
    where the row is above/along/below the center plate, and within each row,
    the plates are arranged East to West.

    The middle entry of the "along" row is the target AtlasPlate instance.
    """
    rows = []
    plates_in_row = []
    row_dec = None
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

def plate_list():
    """
    Create the canonical list of plates based on their defined (RA, Dec) centers,
    since they're defined algorithmically.

    1. Each band of plates is 15 degrees apart in declination (90, 75, 60, etc.)
    2. Within each band M plates are defined (1, 12, 16, etc.);  this corresponds
        to a difference in RA (e.g., at ±30° there are 24 plates separated by 1h RA).
    """
    ldec = [90, 75, 60, 45, 30, 15, 0, -15, -30, -45, -60, -75, -90]
    lsize = [1, 12, 16, 20, 24, 32, 48, 32, 24, 20, 16, 12, 1]
    mul = [0., 2.0, 1.5, 1.2, 1.0, 0.75, 0.5, 0.75, 1.0, 1.2, 1.5, 2.0, 0.]
    plate = {}
    j = 1
    for i in range(len(ldec)):
        dec = ldec[i]
        if abs(dec) == 90:
            plate[j] = (0, dec)
            j += 1
            continue
        ras = [x * mul[i] for x in range(lsize[i])]
        for ra in ras:
            plate[j] = (ra, dec)
            j += 1
    return plate


