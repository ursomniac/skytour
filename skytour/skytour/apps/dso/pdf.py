from reportlab.pdfgen import canvas
from ..observe.pdf import DEFAULT_BOLD, DEFAULT_FONT, DEFAULT_FONT_SIZE
from ..pdf.utils import PAGE_WIDTH, PAGE_HEIGHT, X0, bold_text, long_text, add_image

def create_pdf_page(dso):
    dir = 'dso_pdf/'
    lname = dso.shown_name.lower().replace(' ','_')
    lname = lname.replace('/', '_')
    filename = f'{dir}{dso.pk}__{lname}.pdf'
    p = canvas.Canvas('media/'+filename)

    y = 800
    # Title
    p, tw = bold_text(p, X0, y, dso.shown_name, size=16)
    # Nickname
    if dso.nickname is not None:
        p, tw = bold_text(p, 200, y, dso.nickname, size=14)
    # Priority
    priority = 'None' if dso.priority is None else dso.priority
    p, tw = bold_text(p, 400, y, "Priority: ")
    p.drawString(400 + tw, y, priority)
    y -= 15
    # Aliases
    p.drawString(X0, y, dso.alias_list)

    # RA/Dec
    y -= 25
    p, tw = bold_text(p, X0, y, 'R.A.: ')
    p.drawString(X0 + tw, y, dso.ra_text)
    p, tw = bold_text(p, 200, y, 'Dec.: ')
    p.drawString(200 + tw, y, dso.dec_text)
    # Type / Morph.
    p, tw = bold_text(p, 400, y, 'Type: ')
    mtype = '' if dso.morphological_type is None else dso.morphological_type
    otype = f"{dso.object_type.short_name} {mtype}"
    p.drawString(400 + tw, y, otype)
    # Mag/Ang Size/Surf.Br.
    y -= 20
    p, tw = bold_text(p, X0, y, 'Mag: ')
    mag = '' if dso.magnitude is None else f"{dso.magnitude:.2f}"
    p.drawString(X0 + tw, y, mag)
    p, tw = bold_text(p, 200, y, 'Surf. Br.: ')
    sbr = '' if dso.surface_brightness is None else f'{dso.surface_brightness:.2f}'
    p.drawString(200 + tw, y, sbr)
    p, tw = bold_text(p, 400, y, 'Ang. Size.: ')
    asize = '' if dso.angular_size is None else dso.angular_size
    p.drawString(400 + tw, y, asize)
    # Distance/Units
    y -= 20
    p, tw = bold_text(p, X0, y, 'Dist.: ')
    if dso.distance is not None:
        p.drawString(X0 + tw, y, f"{dso.distance} {dso.distance_units}")
    p, tw = bold_text(p, 200, y, 'Constellation: ')
    p.drawString(200 + tw, y, dso.constellation.name)
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