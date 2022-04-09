import textwrap
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.rl_config import defaultPageSize

PAGE_WIDTH = defaultPageSize[0]
PAGE_HEIGHT = defaultPageSize[1]
X0 = 50

DEFAULT_FONT_SIZE = 12
DEFAULT_FONT = 'Helvetica'
DEFAULT_BOLD = 'Helvetica-Bold'
DEFAULT_ITAL = 'Helvetica'

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

def long_text(p, limit, x, y, text, dy=15, size=10):
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