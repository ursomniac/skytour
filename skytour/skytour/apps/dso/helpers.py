import math
from .atlas_utils import plate_list, get_sep
from .models import DSOList, AtlasPlate, DSO, AtlasPlateVersion
from .plot import create_atlas_plot

def create_dso_list_from_queryset(dsos, name='Default Name', description=None):
    """
    Given a queryset of DSO objects, create a new DSOList instance.
    """
    x = DSOList()
    x.name = name
    x.description = description
    x.save()
    x.dso.add(*dsos)
    x.save()
    return x

def deal_with_version(fn, plate, shapes=False, reversed=False):
    """
    Create/Update an AtlasPlateVersion instance for a given plate whose image is located at fn.
    """
    v = AtlasPlateVersion.objects.filter(
        plate = plate, shapes = shapes, reversed = reversed
    ).first()
    if v is None:
        v = AtlasPlateVersion()
        v.plate = plate
        v.shapes = shapes
        v.reversed = reversed
    v.image.name = 'atlas_images/' + fn
    v.save()

def create_atlas_plate(plate_id, shapes=False, reversed=False):
    """
    Create/Update an AtlasPlate instance with a newly-generated image.
    """
    plates = plate_list()
    x = AtlasPlate.objects.filter(plate_id=plate_id).first()
    if x is None:
        x = AtlasPlate()
    x.plate_id = plate_id
    if plate_id not in plates.keys():
        return None
    ra, dec = plates[plate_id]
    x.center_ra = ra
    x.center_dec = dec
    fn, dso_list = create_atlas_plot(ra, dec, plate_id, shapes=shapes, reversed=reversed)
    x.save()

    # Store everything in AtlasPlateVersion
    v = deal_with_version(fn, x, shapes=shapes, reversed=reversed)
    # Add DSO list
    x.dso.add(*dso_list)
    x.save()
    return x

def lookup_dso(name):
    """
    Look up a DSO based on its name.
    First, test against the shown_name field (canonical name).
    If that fails, test again the list of aliases.
    """
    d = DSO.objects.filter(shown_name=name).first()
    if d is None:
        d = DSO.objects.filter(aliases__shown_name=name).first()
    return d

def get_map_parameters(dso_list, mag=2.4, debug=False):
    """
    Given a list of DSOs, return:
       1. The center ra, dec
       2. The radius of the extent of the list from the center.
    """
    # Phase 1: create X, Y, Z coordinates for each DSO.
    xx = 0.
    yy = 0.
    zz = 0.
    n = 0
    
    for d in dso_list:
        zr = math.radians(d.ra * 15.) # convert to degrees
        zd = math.radians(d.dec)
        xx += math.cos(zd) * math.cos(zr)
        yy += math.cos(zd) * math.sin(zr)
        zz += math.sin(zd)
        n += 1
    xm = xx / n
    ym = yy / n
    zm = zz / n
    ra = math.degrees(math.atan2(ym, xm)) / 15.
    ra %= 24.
    hyp = math.sqrt(xm * xm + ym * ym)
    dec = math.degrees(math.atan2(zm, hyp))
    zra = math.radians(ra * 15.)
    zdec = math.radians(dec)

    if debug: 
        print(f"RA: {ra}  DEC: {dec}")
    # Phase 2: get FOV from distances from this center
    max_dist = None
    for d in dso_list:
        dist = get_sep(zra, zdec, math.radians(d.ra*15.), math.radians(d.dec))
        if debug:
            print(f"RA: {d.ra} DEC: {d.dec} SEP: {dist}")
        if max_dist is None:
            max_dist = dist
        elif dist > max_dist:
            max_dist = dist

    fov = max_dist * mag
    if debug:
        print(f"MAX DIST: {max_dist} FOV: {fov}")
    return ra, dec, max_dist, fov


def get_star_mag_limit(radius):
    if radius < 15:
        return 7
    elif radius < 30:
        return 6
    return 5