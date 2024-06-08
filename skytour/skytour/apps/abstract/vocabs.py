SEEING_CHOICES = (
    (5, '5 = Excellent: stable diffraction rings'),
    (4, '4 = Good: light undulations across diffraction rings'),
    (3, '3 = Fair: broken diffraction rings; central disk deformations'),
    (2, '2 = Poor: (partly) missing diffraction rings; eddy streams in central disk'),
    (1, '1 = Fail: boiling image; no sign of diffraction pattern')
)

IMAGING_STATUS_CHOICES = (
    (0, 'No Images'),
    (1, 'Image Taken'),
    (2, 'Multiple Images Taken')
)

IMAGING_PROCESSING_CHOICES = (
    ('None', 'Not Yet Started'),
    ('Default', 'Default Unistellar/Seestar Image'),
    ('3-Step', '3-Step: Dark, Stretched, Cleaned'),
    ('Pix+RCA', 'Pixinsight + RC Astro'),
    ('DB', 'Processed image added to DB'),
    ('Rejected', 'Image Rejected'),
    ('Unknown', 'Unknown')
)

IMAGE_STYLE_CHOICES = (
    ('square', 'Square Image'), # Use in galleries/carousel
    ('map', 'Annotated Image'), # Use in field panel
    ('full', 'Full Frame Image'), # Use in field panel
    ('other', 'Other'), # Use in carousel?
    # ('finder', 'Finder'), # Use in field panel
)

IMAGE_TYPE_CHOICES = (
    ('e-crop', 'eQuinox 2: Cropped'),
    ('e-full', 'eQuinox 2: Full'),
    ('s-full', 'Seestar S50: Full')
)

IMAGE_POST_OPTIONS = (
    ('None', 'Raw'),
    ('annotated', 'Annotated'),
    ('processed', 'Processed')
)

YES_NO = [(1, 'Yes'), (0, 'No')]
YES = 1
NO = 0