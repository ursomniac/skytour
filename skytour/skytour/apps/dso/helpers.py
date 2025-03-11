import math
from ..astro.utils import get_sep
from .atlas_utils import plate_list
from .models import DSOList, AtlasPlate, DSO, AtlasPlateVersion, AtlasPlateSpecial, AtlasPlateSpecialVersion
from .plot import create_atlas_plot
from .vocabs import SIMPLE_DSO_LIST

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

def deal_with_version(fn, plate, shapes=False, reversed=False, special=False):
    """
    Create/Update an AtlasPlateVersion instance for a given plate whose image is located at fn.
    """
    model = AtlasPlateSpecialVersion if special else AtlasPlateVersion
    path = 'atlas_images_special' if special else 'atlas_images' 
    v = model.objects.filter(
        plate = plate, shapes = shapes, reversed = reversed
    ).first()
    if v is None:
        v = model()
        v.plate = plate
        v.shapes = shapes
        v.reversed = reversed
    v.image.name = f'{path}/{fn}'
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

def create_special_atlas_plate(plate_id, shapes=False, reversed=False):
    """
    Create/Update an AtlasPlate instance with a newly-generated image.
    """
    x = AtlasPlateSpecial.objects.filter(plate_id=plate_id).first()
    if x is None:
        print(f"Plate ID: {plate_id} invalid")
        return None
    x.plate_id = plate_id

    fn, dso_list = create_atlas_plot(
        x.center_ra, x.center_dec, plate_id, fov=x.radius*2., 
        shapes=shapes, reversed=reversed,
        model=AtlasPlateSpecial
    )
    x.save()

    # Store everything in AtlasPlateVersion
    v = deal_with_version(fn, x, shapes=shapes, reversed=reversed, special=True)
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

    hyp = math.sqrt(xm * xm + ym * ym)
    # Dec in degrees
    dec = math.degrees(math.atan2(zm, hyp))
    # Dec in radians
    zdec = math.radians(dec)
    # RA in hours
    ra = math.degrees(math.atan2(ym, xm)) / 15.
    ra %= 24.
    # RA in radians
    zra = math.radians(ra * 15.)

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

    max_dist = max_dist if max_dist > 2. else 2.
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

def get_simple_dso_list():
    """
    SIMPLE_DSO_LIST are the brightest/most popular DSOs (more or less)
    used in the "simple" version of StarMap.  It's not likely to change (much)
    though it COULD be customized if needed.
    """
    dso_list = DSO.objects.filter(pk__in=SIMPLE_DSO_LIST)
    return dso_list