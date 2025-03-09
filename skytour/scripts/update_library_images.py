from skytour.apps.dso.models import DSOLibraryImage
from skytour.apps.solar_system.models import AsteroidLibraryImage, CometLibraryImage, PlanetLibraryImage
from skytour.apps.tech.models import Telescope

telescopes = Telescope.objects.all()
# 2 = eQuinox; 3 = Seestar 50


def process_image(obj):
    # get the old things
    # square -> square; full/map -> landscape; other -> None; ? ---> portrait
    image_style = obj.image_style
    #
    image_alterations = obj.image_alterations
    #
    processing_status = obj.processing_status
    # e-crop/e-full/s-crop/s-full
    image_type = obj.image_type

    # image_orientation 
    if image_style == 'square':
        obj.image_orientation = 'square'
    elif image_style in ['full', 'map']:
        obj.image_orientation = 'landscape'
    elif image_style == 'other':
        obj.image_orientation = 'other'

    # image_processing_status
    if processing_status in ['None', 'Default']:
        obj.image_processing_status = 'default'
    elif processing_status in ['DB', 'Pix+RCA', '3-Step']:
        obj.image_processing_status = 'post-processed'
    elif processing_status == 'Rejected':
        obj.image_processing_status = 'rejected'

    # telescope
    tpk = None
    ori = None
    if image_type is not None:
        t = image_type[0]
        if t[0] == 's':
            tpk = 3
        elif t[0] == 'e':
            tpk = 2
        else:
            tpk = None
        ori = image_type.split('-')[1]
    if tpk is not None:
        obj.telescope_id = tpk

    # image_cropping
    if ori == 'crop':
        obj.image_cropping = 'cropped'
    elif ori == 'full':
        obj.image_cropping = 'full'
    
    return obj

def process_all_objects(model):
    MODELS = {'dso': DSOLibraryImage, 'asteroid': AsteroidLibraryImage, 
              'comet': CometLibraryImage, 'planet': PlanetLibraryImage}
    images = MODELS[model].objects.all()
    for image in images:
        new_image = process_image(image)
        if model == 'dso':
            name = new_image.object.shown_name
        else:
            name = new_image.object.name
        print(f"Updating image {new_image.pk} for {name}")
        new_image.save()
