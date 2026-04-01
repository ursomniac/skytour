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

SYMBOLS = {
    'A-s':'🄰', 'B-s':'🄱', 'C-s':'🄲', 'D-s':'🄳', 'E-s':'🄴', 'F-s':'🄵', 'G-s':'🄶', 
    'H-s':'🄷', 'I-s':'🄸', 'J-s':'🄹', 'K-s':'🄺', 'L-s':'🄻', 'M-s':'🄼', 
    'N-s':'🄽', 'O-s':'🄾', 'P-s':'🄿', 'Q-s':'🅀', 'R-s':'🅁', 'S-s':'🅂',
    'T-s':'🅃', 'U-s':'🅄', 'V-s':'🅅', 'W-s':'🅆', 'X-s':'🅇', 'Y-s':'🅈', 'Z-s':'🅉',

    'A-c':'Ⓐ', 'B-c':'Ⓑ', 'C-c':'Ⓒ', 'D-c':'Ⓓ', 'E-c':'Ⓔ', 'F-c':'Ⓕ', 'G-c':'Ⓖ',
    'H-c':'Ⓗ', 'I-c':'Ⓘ', 'J-c':'Ⓙ', 'K-c':'Ⓚ', 'L-c':'Ⓛ', 'M-c':'Ⓜ', 
    'N-c':'Ⓝ', 'O-c':'Ⓞ', 'P-c':'Ⓟ', 'Q-c':'Ⓠ', 'R-c':'Ⓡ', 'S-c':'Ⓢ', 
    'T-c':'Ⓣ', 'U-c':'Ⓤ', 'V-c':'Ⓥ', 'W-c':'Ⓦ', 'X-c':'Ⓧ', 'Y-c':'Ⓨ', 'Z-c':'Ⓩ', 

    'a-c':'ⓐ', 'b-c':'ⓑ', 'c-c':'ⓒ', 'd-c':'ⓓ', 'E-c':'ⓔ', 'f-c':'ⓕ', 'g-c':'ⓖ', 
    'h-c':'ⓗ', 'i-c':'ⓘ', 'j-c':'ⓙ', 'k-c':'ⓚ', 'L-c':'ⓛ', 'm-c':'ⓜ', 
    'n-c':'ⓝ', 'o-c':'ⓞ', 'p-c':'ⓟ', 'q-c':'ⓠ', 'R-c':'ⓡ', 's-c':'ⓢ', 
    't-c':'ⓣ', 'u-c':'ⓤ', 'v-c':'ⓥ', 'w-c':'ⓦ', 'X-c':'ⓧ', 'y-c':'ⓨ', 'z-c':'ⓩ', 

    '0-c':'⓪', '1-c':'⓵', '2-c':'⓶', '3-c':'⓷', '4-c':'⓸', '5-c':'⓹', 
    '6-c':'⓺', '7-c':'⓻', '8-c':'⓼', '9-c':'⓽', '10-c':'⓾',
}