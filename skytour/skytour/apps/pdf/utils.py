import textwrap
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.rl_config import defaultPageSize

PAGE_WIDTH = defaultPageSize[0]
PAGE_HEIGHT = defaultPageSize[1]
X0 = 50
Y0 = 750

DEFAULT_FONT_SIZE = 12
DEFAULT_FONT = 'Helvetica'
DEFAULT_BOLD = 'Helvetica-Bold'
DEFAULT_ITAL = 'Helvetica'

def copy(item):
    is_str = isinstance(item, str)
    copy = item if is_str else item[0]
    return copy

def size(item):
    is_str = isinstance(item, str)
    size = DEFAULT_FONT_SIZE if is_str else item[1]
    return size

def label_and_text(p, x, y, label, text, cr=15):
    """
    label and text are either string or a tuple (string, font_size):
        (text, [font_size])
    """
    p, tw = bold_text(p, x, y, copy(label), size=size(label))
    if text is not None:
        p = place_text(p, x + tw, y, copy(text), size=size(text))
    if cr > 0:
        y -= cr
    return p, y

def place_text(p, x, y, text, size=DEFAULT_FONT_SIZE):
    p.setFont(DEFAULT_FONT, size)
    text = '' if text is None else text
    p.drawString(x, y, text)
    return p

def bold_text (p, x, y, text, size=14):
    p.setFont(DEFAULT_BOLD, size)
    text = '' if text is None else text
    p.drawString(x, y, text)
    p.setFont(DEFAULT_FONT, DEFAULT_FONT_SIZE)
    tw = stringWidth(text, DEFAULT_BOLD, size)
    return p, tw

def add_image(p, y, file, x=50, size=250):
    if file is not None:
        map_img = ImageReader(file)
        p.drawImage(map_img, x, y-size, width=size, height=size, preserveAspectRatio=True)
    return p, y - size

def long_text(p, limit, x, y, text, dy=15, size=8):
    p.setFont(DEFAULT_FONT, size)
    text = '' if text is None else text
    text = text.replace('\r', '')
    pass1 = text.split('\n')

    lines = []
    for line in pass1:
        if len(line.strip()) == 0:
            continue
        if len(line) > limit:
            nlines = textwrap.wrap(line, width=limit)
            lines += nlines
        else:
            lines.append(line)

    for line in lines:
        p.drawString(x, y, line)
        y -= dy

    p.setFont(DEFAULT_FONT, DEFAULT_FONT_SIZE)
    return p, y