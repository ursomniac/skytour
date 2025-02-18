SEEING_CHOICES = (
    (5, '5 = Excellent: stable diffraction rings'),
    (4, '4 = Good: light undulations across diffraction rings'),
    (3, '3 = Fair: broken diffraction rings; central disk deformations'),
    (2, '2 = Poor: (partly) missing diffraction rings; eddy streams in central disk'),
    (1, '1 = Fail: boiling image; no sign of diffraction pattern')
)

# TODO V2: Clean this up
#   - None / Default / ??? --- is there a notes field?
IMAGING_PROCESSING_CHOICES = (
    ('None', 'Not Yet Started'),
    ('Default', 'Default Unistellar/Seestar Image'),
    ('3-Step', '3-Step: Dark, Stretched, Cleaned'),
    ('Pix+RCA', 'Pixinsight + RC Astro'),
    ('DB', 'Processed image added to DB'),
    ('Rejected', 'Image Rejected'),
    ('Unknown', 'Unknown')
)

# TODO V2: clean this up --- this is used to point to which panel the image is placed.
#   - probably better to DEFINE the panels and make the choices reflect that.
IMAGE_STYLE_CHOICES = (
    ('square', 'Square Image'), # Use in galleries/carousel
    ('map', 'Annotated Image'), # Use in field panel
    ('full', 'Full Frame Image'), # Use in field panel
    ('other', 'Other'), # Use in carousel?
    # ('finder', 'Finder'), # Use in field panel
)

# TODO V2: This is problematic because the library image doesn't "know" about the obs's equipment 
#   So this is a kludge to get around that.
IMAGE_TYPE_CHOICES = (
    ('e-crop', 'eQuinox 2: Cropped'),
    ('e-full', 'eQuinox 2: Full'),
    ('s-full', 'Seestar S50: Full'),
    ('s-crop', 'Seestar S50: Cropped')
)

# TODO V2: the field for this isn't used anywhere!  REMOVE!
IMAGE_POST_OPTIONS = (
    ('None', 'Raw'),
    ('annotated', 'Annotated'),
    ('processed', 'Processed')
)

# TODO V2: Move this to a top-level "general" vocab (I think it is in several places)
YES_NO = [(1, 'Yes'), (0, 'No')]
YES = 1
NO = 0