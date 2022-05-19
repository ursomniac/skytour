from .models import DSOList, AtlasPlate, DSO, AtlasPlateVersion
from .plot import plate_list, create_atlas_plot

def create_dso_list_from_queryset(dsos, name='Default Name', description=None):
    x = DSOList()
    x.name = name
    x.description = description
    x.save()
    x.dso.add(*dsos)
    x.save()
    return x

def deal_with_version(fn, plate, shapes=False, reversed=False):
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
    # Keep this around for now -- TODO: remove this from the model
    #x.plate.name = 'atlas_images/' + fn
    x.save()

    # Store everything in AtlasPlateVersion
    v = deal_with_version(fn, x, shapes=shapes, reversed=reversed)
    # Add DSO list
    x.dso.add(*dso_list)
    x.save()
    return x

def lookup_dso(name):
    d = DSO.objects.filter(shown_name=name).first()
    if d is None:
        d = DSO.objects.filter(aliases__shown_name=name).first()
    return d