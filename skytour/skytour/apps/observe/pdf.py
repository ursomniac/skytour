from reportlab.pdfgen import canvas
from ..pdf.utils import (
    DEFAULT_BOLD, DEFAULT_FONT, DEFAULT_FONT_SIZE, DEFAULT_ITAL,
    PAGE_WIDTH, PAGE_HEIGHT, X0,
    add_image, bold_text, long_text
)


def create_pdf_form(loc):
    dir = 'location_pdf/'
    lname = '' if loc.name is None else f"{loc.name.lower().replace(' ','_')}__"
    filename = f'{dir}{loc.pk}__{lname}{loc.city.lower()}_{loc.state.abbreviation.lower()}.pdf'
    #p = canvas.Canvas(buffer, pagesize=letter) # width = 612, height = 792
    p = canvas.Canvas('media/'+filename)
    x0 = X0
    title = loc.street_address if loc.street_address is not None else ''
    if loc.name is not None:
        title = loc.name + " " + title
    p, tw = bold_text(p, x0, 800, title, size=16)
    # status
    status = loc.status if loc.status != 'TBD' else ''
    p, tw = bold_text(p, 400, 800, f'Status: {status}', size=16)
    
    # city, state
    p, tw = bold_text(p,  x0, 780, f'{loc.city}, {loc.state.abbreviation}')
    # Distance
    p, tw = bold_text(p,  x0, 750, 'Distance: ')
    p.drawString( 50 + tw, 750, f'{loc.travel_distance} mi')
    # travel time
    p, tw = bold_text(p,  x0, 730, 'Travel Time: ')
    p.drawString( 50 + tw, 730, f'{loc.travel_time} min')

    # Latitude
    p, tw = bold_text(p, 200, 750, 'Latitude: ')
    p.drawString(200 + tw, 750, f'{loc.latitude:8.5f}')
    # Longitude
    p, tw = bold_text(p, 200, 730, 'Longitude: ')
    p.drawString(200 + tw, 730, f'{loc.longitude:10.5f}')
    # Elevation
    p, tw = bold_text(p, 200, 710, 'Elevation: ')
    p.drawString(200 + tw, 710, f'{loc.elevation} m')

    # SQM
    p, tw = bold_text(p, 400, 770, 'SQM: ')
    p.drawString(400 + tw, 770, f'{loc.sqm}')
    # Bortle
    p, tw = bold_text(p, 400, 750, f'Bortle: {loc.bortle}')
    # brightness
    p, tw = bold_text(p, 400, 730, 'Bright.: ')
    p.drawString(400 + tw, 730, f'{loc.brightness}')
    # limiting Mag
    p, tw = bold_text(p, 400, 710, 'Lim. Mag: ')
    p.drawString(400 + tw, 710, f'{loc.limiting_magnitude}')

    y = 700
    p.line(50, y, 550, y)

    y = 680
    # Description
    p, tw = bold_text(p, x0, y, 'Description: ')

    p.setFont(DEFAULT_FONT, 10)
    if loc.description:
        p, y = long_text(p, 120, 50, 665, loc.description)
    
    # Google Map
    map_image = None if loc.map_image.name == '' else loc.map_image.file
    p, y = add_image(p, y, map_image)

    # Google Earth
    earth_image = None if loc.earth_image.name == '' else loc.earth_image.file
    p, y = add_image(p, y, earth_image)
    ynew = y - 10

    y = 610
    x = 320
    # Parking
    p, tw = bold_text(p, x, y, 'Parking: ')
    p.drawString(x + tw, y, f'{loc.parking}')
    # Level
    y -= 40
    p, tw = bold_text(p, x, y, 'Level: ')
    p.drawString(x + tw, y, f'{loc.is_flat}')

    # Light Sources
    y -= 40
    p, tw = bold_text(p, x, y, 'Lights: ')
    p, y = long_text(p, 40, x, y-20, loc.light_sources)

    y -= 100
    # Notes
    p, tw = bold_text(p, x, y, 'Notes: ')

    # Horizon
    y = ynew
    p, tw = bold_text(p, 50, y, 'Horizon: ')
    p, y = long_text(p, 100, 50, y-20, loc.horizon_blockage)
    
    y = 40
    p.setFont(DEFAULT_BOLD, 14)
    p.drawString( 75, y, 'N')
    p.drawString(187, y, 'E')
    p.drawString(300, y, 'S')
    p.drawString(412, y, 'W')
    p.drawString(525, y, 'N')
    p.line(50, y+12, 550, y+12)

    p.showPage()
    p.save()
    return filename