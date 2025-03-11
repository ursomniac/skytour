PLANET_CHOICES = [
    ('visible', 'Only Above the Horizon'),
    ('all', 'All Planets')
]

SEEING_CHOICES = (
    (5, '5 = Excellent: stable diffraction rings'),
    (4, '4 = Good: light undulations across diffraction rings'),
    (3, '3 = Fair: broken diffraction rings; central disk deformations'),
    (2, '2 = Poor: (partly) missing diffraction rings; eddy streams in central disk'),
    (1, '1 = Fail: boiling image; no sign of diffraction pattern')
)

SESSION_STAGE_CHOICES = [
    ('start', 'Start'),
    ('during', 'During'),
    ('end', 'End')
]

OBSERVE_TYPES = [
    ('dso', 'DSO'),
    ('planet', 'Planet'), 
    ('asteroid', 'Asteroid'), 
    ('comet', 'Comet'), 
    ('moon', 'Moon'), 
    ('other', 'Other')
]