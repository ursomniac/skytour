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

def fix_ra(ra):
    h = int(ra)
    m = (ra - h) * 60
    m = int(m + 0.5)
    return f"{h:02d}h {m:02d}m"

def create_plate_pdf(plate, fn=None, shapes=True):
    dir = 'atlas_pdf/'
    if fn is None:
        fn = f"plate_{plate.plate_id}.pdf"
        filename = 'media/' + dir + fn
    else:
        filename = f"{fn}.pdf"
    p = canvas.Canvas(filename)
    y = 800

    # Title and Nickname
    p, tw = bold_text(p, X0, y, f"Atlas Plate: {plate.plate_id}", size=16)
    y -= 25
    # RA/Dec
    p, y = label_and_text(p,  X0, y, 'R.A.: ', fix_ra(plate.center_ra), cr=0)
    p, y = label_and_text(p, 200, y, 'Dec: ', f"{plate.center_dec:5.1f}°", cr=0)
    p, y = label_and_text(p, 400, y,'in ', plate.center_constellation.name, cr=15)
    p, y = label_and_text(p,  X0, y, f"Constellations: ", plate.constellation_list, cr=0)
    p, y = label_and_text(p, 400, y, "# DSOs on Plate: ", f"{plate.dso_count}", cr=15)
    image = plate.atlasplateversion_set.get(reversed=False, shapes=shapes)
    image_fn = image.image.file
    p, y = add_image(p, y, image_fn, size=500, x=30)

    y = 240
    if plate.dso_count > 100:
        p, tw = bold_text(p, X0, y, f"DSOs - showing 100 of {plate.dso_count}", size=12)
    else:
        p, tw = bold_text(p, X0, y, f"DSOs - {plate.dso_count} total", size=12)
    y -= 15
    ytop = y
    
    pd = {'Highest': 'H', 'High': 'h', 'Medium': 'm', 'Low': 'l', 'None': ' '}
    qs_sorted = plate.dso.order_by('ra')

    i = 0
    cols = [0, 100, 200, 300, 400]
    for dso in qs_sorted:
        if i >=  100:
            break
        name = '???' if dso.shown_name is None else dso.shown_name
        priority = 'None' if dso.priority is None else dso.priority
        code = ' ' if dso.object_type is None else dso.object_type.code
        x = cols[i // 20] + X0
        y = ytop - 10 * (i % 20)
        p, y = label_and_text(p, x +  0, y, "", (f"{name}", 7), cr=0)
        p, y = label_and_text(p, x + 50, y, "", (f"{code}", 7), cr=0)
        p, y = label_and_text(p, x + 75, y, "", (f"{pd[priority]}", 7), cr=0)
        i += 1

    p.showPage()
    p.save()
    return filename