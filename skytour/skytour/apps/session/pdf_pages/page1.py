from reportlab.pdfbase.pdfmetrics import stringWidth
from ...astro.calendar import get_upcoming_calendar
from ...solar_system.meteors import get_meteor_showers
from ...solar_system.helpers import get_adjacent_planets
from ...utils.format import to_sex
from .vocabs import PAGE_WIDTH

def do_page1(p, context):
    cookie_dict = context['cookies']
    utdt = context['utdt_start']
    location = context['location']
    ### PAGE 1 - the Overall stuff
    # Title
    p.setFont('Helvetica-Bold', 24)
    p.drawCentredString(PAGE_WIDTH/2, 720, "SKYTOUR")
    p.setFont('Helvetica', 12)

    # Metadata: UTDT, location, etc.
    # UTDT Start
    utdt_str = context['utdt_start'].strftime("%Y-%m-%d %H:%M")
    tw = stringWidth('UTDT: ', 'Helvetica-Bold', 12)
    p.setFont('Helvetica-Bold', 12)
    p.drawString(50, 650, 'UTDT: ')
    p.setFont('Helvetica', 12)
    p.drawString(50 + tw + 5, 650, utdt_str)
    # Location
    address = f'{location.city}, {location.state.abbreviation}'
    if location.name:
        address = location.name + ', ' + address
    tw = stringWidth('Location: ', 'Helvetica-Bold', 12)
    p.setFont('Helvetica-Bold', 12)
    p.drawString(50, 625, 'Location: ')
    p.setFont('Helvetica', 12)
    p.drawString(50 + tw + 5, 625, address)
    # Latitude:
    tw = stringWidth('Longitude', 'Helvetica-Bold', 12)
    p.setFont('Helvetica-Bold', 12)
    p.drawString(300, 650, 'Latitude: ')
    p.drawString(300, 625, 'Longitude: ')
    p.setFont('Helvetica', 12)
    p.drawString(300 + tw + 5, 650, to_sex(location.latitude, format="degrees"))
    p.drawString(300 + tw + 5, 625, to_sex(location.longitude, format="degrees"))

    # FORM for initial conditions: Temp, Hum, SQM, Wind, Seeing, Setup stars?
    y = 575
    p.setFont('Helvetica-Bold', 14)
    p.drawString(50, y, 'Initial Conditions:')
    p.setFont('Helvetica-Bold', 12)
    p.drawString(50, y-30, 'Time: _______________')
    p.drawString(50, y-60, 'SQM:  _______________')
    p.drawString(200, y-60, 'Clouds:  ___________________________________________')
    p.drawString(50, y-90, "Temp: _______________")
    p.drawString(200, y-90, "Rel. Hum.:  ___________")
    p.drawString(350, y-90, 'Wind:    ____________________')
    p.drawString(50, y-120, 'Seeing: ______________')
    p.setFont('Helvetica', 12)
    y -= 200
    # Calendar
    y -= 50
    p.setFont('Helvetica-Bold', 14)
    p.drawString(50, y, 'Calendar:')
    p.setFont('Helvetica', 10)
    y -= 30
    events = get_upcoming_calendar(context['utdt_start'])
    if len(events) > 0:
        for e in events:
            p.drawString(50, y, e.date.strftime('%b %-d'))
            if e.time:
                p.drawString(150, y, e.time.strftime('%H:%M')+' UT')
            if e.event_type:
                p.drawString(250, y, e.event_type.name)
            p.drawString(350, y, e.title.encode('UTF-8'))
            y -= 15
    else:
        p.drawString(50, y, '(no Events)')

    # Meteor Showers
    y -= 30
    p.setFont('Helvetica-Bold', 14)
    p.drawString(50, y, 'Meteor Showers:')
    p.setFont('Helvetica', 10)
    y -= 30
    meteors = get_meteor_showers(utdt)
    if len(meteors) > 0:
        for ms in meteors:
            p.drawString(50, y, ms.name)
            z = f'{ms.start_date.month_name[:3]} {ms.end_date.day} to '
            z += f'{ms.end_date.month_name[:3]} {ms.end_date.day} '
            p.drawString(150, y, z)
            z = f'Peak: {ms.peak_date.month_name[:3]} {ms.peak_date.day}'
            p.drawString(250, y, z)
            p.drawString(350, y, str(ms.zhr) + ' ZHR')
            y -= 15
    else:
        p.drawString(50, y, '(no meteor showers)')
    # Planets Close Together
    y -= 45
    p.setFont('Helvetica-Bold', 14)
    p.drawString(50, y, 'Planets Close Together:')
    p.setFont('Helvetica', 10)
    y -= 30
    adj_planets = get_adjacent_planets(cookie_dict['planets'], utdt)
    if len(adj_planets) > 0:
        for ap in adj_planets:
            z = f'{ap[0]} is {ap[2]:.1f}° from {ap[1]}'
            p.drawString(50, y, z)
            y -= 15
    else:
        p.drawString(50, y, "(No planets within 10° of each other")
    p.showPage()
    return p