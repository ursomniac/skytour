from reportlab.pdfgen import canvas
from ..observe.pdf import DEFAULT_BOLD, DEFAULT_FONT, DEFAULT_FONT_SIZE
from ..pdf.utils import (
    PAGE_WIDTH, PAGE_HEIGHT, X0, 
    bold_text, long_text, add_image,
    label_and_text
)
def create_pdf_page(dso, fn=None):
    dir = 'dso_pdf/'
    lname = dso.shown_name.lower().replace(' ','_')
    lname = lname.replace('/', '_')
    if fn is None:
        filename = f'{dir}{dso.pk}__{lname}.pdf'
    else:
        filename = f'{fn}.pdf'
    p = canvas.Canvas('media/'+filename)

    y = 800
    # Title and Nickname
    p, tw = bold_text(p, X0, y, dso.shown_name, size=16)
    if dso.nickname is not None:
        p, tw = bold_text(p, 200, y, dso.nickname, size=14)
    # Priority
    priority = 'None' if dso.priority is None else dso.priority
    p, y = label_and_text(p, 400, y, 'Priority: ', priority)
    # Aliases
    p.drawString(X0, y, dso.alias_list)
    y -= 25

    # RA/Dec
    p, y = label_and_text(p, X0, y, 'R.A.: ', dso.ra_text, cr=0)
    p, y = label_and_text(p, 200, y, 'Dec: ', dso.dec_text, cr=0)
    # Type / Morph.
    mtype = '' if dso.morphological_type is None else dso.morphological_type
    otype = f"{dso.object_type.short_name} {mtype}"
    p, y = label_and_text(p, 400, y, 'Type: ', otype, cr=20)
    # Mag/Ang Size/Surf.Br.
    mag = '' if dso.magnitude is None else f"{dso.magnitude:.2f}"
    p, y = label_and_text(p, X0, y, 'Mag: ', mag, cr=0)
    sbr = '' if dso.surface_brightness is None else f'{dso.surface_brightness:.2f}'
    p, y = label_and_text(p, 200, y, 'Surf. Br.: ', sbr, cr=0)
    asize = '' if dso.angular_size is None else dso.angular_size
    p, y = label_and_text(p, 400, y, 'Ang. Size: ', asize, cr=20)
    # Distance/Units
    dstr = f'{dso.distance} {dso.distance_units}' if dso.distance is not None else ''
    p, y = label_and_text(p, X0, y, 'Dist.: ', dstr, cr=0)
    p, y == label_and_text(p, 200, y, 'Constellation: ', dso.constellation.name, cr=10)
    y -= 10
    p.line(50, y, 550, y)
    y -= 10
    
    # Finder Chart
    ytop = y
    finder = None if dso.dso_finder_chart.name == '' else dso.dso_finder_chart.file
    p, y = add_image(p, ytop, finder, size=300, x=30)
    y2 = y
    # Notes
    y = ytop -10
    p, tw = bold_text(p, 350, y, 'Notes: ')
    y -= 15
    p, y = long_text(p, 40, 350, y, dso.notes)
    # FOV
    y = y2
    fov = None if dso.field_view.name == '' else dso.field_view.file
    p, y = add_image(p, y, fov)
    ybottom = y
    # Image
    y = y2
    pix = dso.images.first()
    if pix is not None:
        p, y = add_image(p, y2, pix.image.file, x=320)


    p.showPage()
    p.save()
    return filename