from dateutil.parser import isoparse
from ...pdf.utils import label_and_text
from ...site_parameter.helpers import find_site_parameter
from ...solar_system.models import Asteroid, Comet, Planet
from ...solar_system.plot import create_planet_system_view, create_finder_chart
from ...utils.format import to_sex, to_hm, to_dm, to_time
from .utils import do_line, show_object_table, show_table_header
from .vocabs import PDICT, PLANET_LIST

FCX = [390, 30, 210, 390, 30, 210, 390, 30, 210, 390]
FCY = [-45, 130, 130, 130, 310, 310, 310, 490, 490, 490]

def do_planets(p, context):
    utdt = context['utdt_start']
    cookie_dict = context['cookies']

    y = 720
    p.setFont('Helvetica-Bold', 14)
    p.drawString(50, y, 'Planets:')
    p.setFont('Helvetica', 10)
    y -= 30

    for planet in PLANET_LIST:
        instance = Planet.objects.get(slug=planet.lower())
        tp = cookie_dict['planets'][planet]
        y =  PDICT[planet]['y0']
        xp = PDICT[planet]['xp']
        yp = PDICT[planet]['yp']
        p.setFont('Helvetica-Bold', 12)
        p.drawString(50, y, planet)
        p.setFont('Helvetica', 10)
        p.drawString(120, y, 'in ' + tp['observe']['constellation']['abbr'])
        p.drawString(160, y, f"R.A.: {to_hm(tp['apparent']['equ']['ra'])}")
        y -= 15
        p.drawString(160, y, f"Dec. {to_dm(tp['apparent']['equ']['dec'])}")
        y -= 15
        dy = y + 8 # save for later
        p.drawString(160, y, f"Dist: {tp['apparent']['distance']['au']:.2f} AU")
        y -= 15
        p.drawString(160, y, f"Mag: {tp['observe']['apparent_magnitude']:.2f}")
        y -= 15
        p.drawString(160, y, f"Ang. Size: {tp['observe']['angular_diameter_str']}")
        tel_view, _ = create_planet_system_view(utdt, instance, cookie_dict['planets'], reversed=False)
        p.drawInlineImage(tel_view, xp, yp, 180, 180)
        if planet == 'Neptune':
            nft, _ = create_finder_chart(
                utdt, 
                instance, 
                cookie_dict['planets'],
                cookie_dict['asteroids'],
                reversed = False
            )
            p.drawInlineImage(nft, 420, 20, 180, 180)
        for alm in tp['almanac']:
            p.drawString(65, dy, f"{alm['type']}: {isoparse(alm['ut']).strftime('%H:%M')} UT")
            dy -= 15
    p.showPage() # This is page 3

    return p

def do_asteroids(p, context):
    utdt = context['utdt_start']
    cookie_dict = context['cookies']

    y = 720
    p.setFont('Helvetica-Bold', 14)
    p.drawString(50, y, 'Asteroids:')
    p.setFont('Helvetica', 8)
    y -= 15

    n_asteroids = len(cookie_dict['asteroids'])
    if n_asteroids > 0:
        na = 0
        fcy_start = y - n_asteroids * 15
        p, y = show_table_header(p, y)
        for a in cookie_dict['asteroids']:
            ses = a['session']
            is_up = ses['start']['is_up'] or ses['end']['is_up']
            if not is_up:
                continue
            instance = Asteroid.objects.get(slug=a['slug'])
            p, y = show_object_table(a, p, y, instance)
            # Finder Charts
            if na < 10:
                aft, _ = create_finder_chart(
                    utdt, 
                    instance, 
                    planets_cookie=cookie_dict['planets'],
                    asteroids=cookie_dict['asteroids'],
                    object_type='asteroid',
                    obj_cookie=a,
                    fov=5,
                    reversed = False
                )
                p.drawInlineImage(aft, FCX[na], fcy_start - FCY[na], 180, 180)
                na += 1
    else:
        p.drawString(50, y, '(no Asteroids)')
    p.showPage() # This is page 4

    return p


def do_comets(p, context):
    cookie_dict = context['cookies']
    utdt = context['utdt_start']

    y = 720
    p.setFont('Helvetica-Bold', 14)
    p.drawString(50, y, 'Comets:')
    p.setFont('Helvetica', 8)
    y -= 30
    
    n_comets = len(cookie_dict['comets'])
    nc = 0
    na = 1 # fudge the position of the first finder chart
    if n_comets > 0:
        fcy_start = y - n_comets * 15 - 20
        p, y = show_table_header(p, y, xoff=40)
        for comet in cookie_dict['comets']:
            ses = comet['session']
            is_up = ses['start']['is_up'] or ses['end']['is_up']
            bright_enough = comet['observe']['apparent_magnitude'] <= 12.0
            if not is_up or not bright_enough:
                continue
            nc += 1
            instance = Comet.objects.get(pk=comet['pk']) 
            p, y = show_object_table(comet, p, y, instance, xoff=40)
            
            if na < 6:
                aft, _ = create_finder_chart(
                    utdt, 
                    instance, 
                    planets_cookie=cookie_dict['planets'],
                    asteroids=cookie_dict['asteroids'],
                    object_type='comet',
                    obj_cookie=comet,
                    fov=5,
                    reversed = False
                )
                p.drawInlineImage(aft, FCX[na], fcy_start - FCY[na], 180, 180)
                na += 1        
    if nc == 0:
        p.drawString(50, y, '(no comets)')
    
    y -= FCY[na] + 60
    p.showPage()
    return p

def do_moon(p, context):
    cookie_dict = context['cookies']
    utdt = context['utdt_start']

    y_start = 720
    y = y_start
    p.setFont('Helvetica-Bold', 16)
    p.drawString(50, y, 'Moon:')
    p.setFont('Helvetica', 12)
    y -= 30
    ytop = y
    obs = cookie_dict['moon']['observe']
    ses = cookie_dict['moon']['session']
    app = cookie_dict['moon']['apparent']
    for s in [
        ("in: ", f"{obs['constellation']['name']}", 24),
        ("RA: ", f"{app['equ']['ra_str']}", 16),
        ("Dec: ", f"{app['equ']['dec_str']}", 24),
        ("Phase: ",f"{obs['lunar_phase']['phase']}", 16),
        ("Illum.: ",f"{obs['fraction_illuminated']:.1f}%", 24),
        ("Dist.: ",f"{app['distance']['km']:.1f} km", 16),
        ("Light Time: ",f"{to_time(app['distance']['light_time'])}", 16),
        ("Mag: ",f"{obs['apparent_magnitude']:.2f}", 24)

    ]:
        p, y = label_and_text(p, 50, y, (s[0], 12), (s[1], 12), cr=s[2])

    for alm in cookie_dict['moon']['almanac']:
        l = f"{alm['type']}: "
        t = f"{isoparse(alm['local_time']).strftime('%H:%M %p')} {context['time_zone']}"
        p, y = label_and_text(p, 50, y, (l, 12), (t, 12), cr=16) 
    # Phase plot
    cookie_dict['moon']['name'] = 'Moon' # TODO: Fix this bug!
    moon_tel, _ = create_planet_system_view(
        utdt,
        None,
        cookie_dict['moon'],
        object_type = 'moon',
        flipped = False,
        reversed = False
    )
    p.drawInlineImage(moon_tel, 30, y -200, 200, 200)
    y =  200

    map = find_site_parameter('simple-moon-map', None, 'image')
    p.drawImage(map.file.name, 250, 450, width=300, height=300, mask=None)

    sqm = find_site_parameter('moon-vs-sqm', None, 'image')
    y -= 150
    p.drawImage(sqm.file.name, 50, y, width=500,  height=.46*500, mask=None)
    p.showPage()

    return p