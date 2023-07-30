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
    ('DB', 'Processed image added to DB'),
    ('Rejected', 'Image Rejected'),
    ('Unknown', 'Unknown')
)

YES_NO = [(1, 'Yes'), (0, 'No')]
YES = 1
NO = 0