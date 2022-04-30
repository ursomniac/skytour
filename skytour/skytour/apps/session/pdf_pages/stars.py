import datetime
from ...stars.plot import get_skymap, get_zenith_map
from .vocabs import PAGE_WIDTH

def do_skymap(p, context):
    cookie_dict = context['cookies']
    location = context['location']

    ######################################### PAGE 2
    # Skymap 
    p.setFont('Helvetica-Bold', 24)
    p.drawCentredString(PAGE_WIDTH/2, 700, 'SKYMAP')
    p.setFont('Helvetica', 12)
    skymap, interesting, last, times = get_skymap(
        context['utdt_start'], location,
        planets = cookie_dict['planets'],
        asteroid_list = cookie_dict['asteroids'],
        comet_list = cookie_dict['comets'],
        moon = cookie_dict['moon'],
        sun = cookie_dict['sun'],
        reversed=False,
        local_time = context['local_time']
    ) 
    p.drawInlineImage(skymap, 28, 150, 7.5*72, 7.5*72)
    p.setFont('Helvetica-Bold', 14)
    p.drawString( 50, 150, 'Planets')
    p.drawString(175, 150, 'Asteroids')
    p.drawString(400, 150, 'Comets')
    p.setFont('Helvetica', 10)

    start_y = 130
    if len(interesting['planets']) > 0:
        for o in interesting['planets']:
            p.drawString(50, start_y, o['name'])
            start_y -= 15
    else:
        p.drawString(50, start_y, "(no planets)")
    start_y = 130
    na = 0
    x = 175
    for a in interesting['asteroids']:
        p.drawString(x, start_y, a['name'])
        start_y -= 15
        na += 1
        if na == 6:
            x = 275
            start_y = 130
    start_y = 130
    if len(interesting['comets']) > 0:
        for c in interesting['comets']:
            p.drawString(400, start_y, c['letter'] + ': ' + c['name'])
            start_y -= 15
    else:
        p.drawString(400, start_y, '(no comets)')

    p.showPage() # This ends the page
    return p

def do_zenith(p, context):
    location = context['location']
    ######################################### PAGE 3
    # Zenith Finding Chart for limiting magnitude
    y = 720
    p.setFont('Helvetica-Bold', 24)
    p.drawCentredString(PAGE_WIDTH/2, 700, 'Zenith Chart')
    p.setFont('Helvetica', 12)
    utdt_mid = context['utdt_start'] + datetime.timedelta(hours=context['session_length']/2.)
    local_mid = context['local_time'] + datetime.timedelta(hours=context['session_length']/2.)
    p.drawString(50, 670, f"{local_mid.strftime('%b %-d, %Y %-I:%M %p %z')}")
    zenith_chart, _ = get_zenith_map(
        utdt_mid,
        location, 
        6.5, # mag limit
        30., # radius from zenith
        reversed=False,
        mag_offset = 0.5
    ) 
    p.drawInlineImage(zenith_chart, 28, 100, 7.5*72, 7.5*72)
    p.showPage() # This ends the page
    return p