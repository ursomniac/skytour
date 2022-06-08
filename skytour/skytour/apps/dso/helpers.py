from .atlas_utils import plate_list
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
    fn, dso_list = create_atlas_plot(
        ra, dec, plate_id, shapes=shapes, reversed=reversed)
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