SEEING_CHOICES = (
    (5, '5 = Excellent: stable diffraction rings'),
    (4, '4 = Good: light undulations across diffraction rings'),
    (3, '3 = Fair: broken diffraction rings; central disk deformations'),
    (2, '2 = Poor: (partly) missing diffraction rings; eddy streams in central disk'),
    (1, '1 = Fail: boiling image; no sign of diffraction pattern')
)

IMAGE_PROCESSING_STATUS_OPTIONS = ( 
    ('default', 'Default'), # as provided from the app
    ('post-processed', 'Post Processed'),
    ('annotated', 'Annotated'),
    ('rejected', 'Rejected'),
    ('unknown', 'Unknown')
)

IMAGE_ORIENTATION_CHOICES = (
    ('square', 'Square'),
    ('mosaic', 'Mosaic'),
    ('landscape', 'Landscape'),
    ('portrait', 'Portait'),
    ('other', 'Other')
)

IMAGE_CROPPING_OPTIONS = (
    ('full', 'Full-Size'),
    ('cropped', 'Cropped')
)

YES_NO = [(1, 'Yes'), (0, 'No')]
YES = 1
NO = 0