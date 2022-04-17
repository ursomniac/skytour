from .models import DSOList, AtlasPlate
from .plot import plate_list, create_atlas_plot

def create_dso_list_from_queryset(dsos, name='Default Name', description=None):
    x = DSOList()
    x.name = name
    x.description = description
    x.save()
    x.dso.add(*dsos)
    x.save()
    return x

def create_atlas_plate(plate_id):
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
    fn, dso_list = create_atlas_plot(ra, dec)
    x.plate.name = 'atlas_images/' + fn
    x.save()
    x.dso.add(*dso_list)
    x.save()
    return x

