import datetime, pytz
import io

from dateutil.parser import isoparse
from django.http import HttpResponse
from django.views.generic import View
from reportlab.lib.pagesizes import letter
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.pdfgen import canvas
from reportlab.rl_config import defaultPageSize

from ..dso.models import DSO
from ..misc.utils import get_upcoming_calendar
from ..site_parameter.helpers import find_site_parameter
from ..solar_system.meteors import get_meteor_showers
from ..solar_system.helpers import get_adjacent_planets
from ..solar_system.models import Planet, Asteroid, Comet
from ..solar_system.plot import create_planet_system_view, create_finder_chart
from ..stars.plot import get_skymap, get_zenith_map
from ..utils.format import to_sex, to_hm, to_dm, to_time

from .cookie import deal_with_cookie, get_all_cookies
from .plan import get_plan

PLANET_LIST = ['Mercury', 'Venus', 'Mars', 'Jupiter', 'Saturn', 'Uranus', 'Neptune']
P_START = [670, 580, 490, 400, 310, 220, 130, 40]

PDICT = {
    'Mercury': dict(y0=670, xp=240, yp=580),
    'Venus':   dict(y0=580, xp=420, yp=580),
    'Mars':    dict(y0=490, xp=240, yp=390),
    'Jupiter': dict(y0=400, xp=420, yp=390),
    'Saturn':  dict(y0=310, xp=240, yp=200),
    'Uranus':  dict(y0=220, xp=420, yp=200),
    'Neptune': dict(y0=130, xp=240, yp=20)
}

def show_dso_header(p, y):
    pass

def show_dso_line(p, y, instance):
    pass

def show_object_table(obj, p, y, instance, xoff=0):
    app = obj['apparent']
    obs = obj['observe']
    p.drawString(50, y, obj['name'])
    p.drawString(120+xoff, y, 'in '+obs['constellation']['abbr'])
    p.drawString(150+xoff, y, to_hm(app['equ']['ra']))
    p.drawString(195+xoff, y, to_dm(app['equ']['dec']))
    p.drawString(230+xoff, y, f"{app['distance']['au']:5.2f}")
    p.drawString(260+xoff, y, f"{to_time(app['distance']['light_time'])}")
    p.drawString(300+xoff, y, f"{obs['apparent_magnitude']:5.2f}")
    if instance.last_observed is not None:
        p.drawString(330+xoff, y, instance.last_observed.strftime('%Y-%m-%d'))
    y -= 12
    return p, y

def show_table_header(p, y, xoff=0):
    p.setFont('Helvetica-Bold', 9)
    p.drawString(50, y, 'NAME')
    p.drawString(120+xoff, y, 'CON.')
    p.drawString(150+xoff, y, 'R.A.')
    p.drawString(195+xoff, y, 'DEC.')
    p.drawString(230+xoff, y, 'DIST')
    p.drawString(260+xoff, y, 'L.T.')
    p.drawString(300+xoff, y, 'MAG')
    p.drawString(330+xoff, y, 'LAST OBS.')
    y -= 15
    p.setFont('Helvetica', 8)
    return p, y

def do_line(p, x, y, l, dy=15):
    p.drawString(x, y, l)
    y -= dy
    return p, y

class PlanPDFView(View):
    def get_context_data(self, **kwargs):
        context = {}
        return context

    def get(self, request, *args, **kwargs):
        context = self.get_context_data()
        context = deal_with_cookie(request, context)
        utdt = context['utdt_start']
        cookie_dict = context['cookies'] = get_all_cookies(request)
        context = get_plan(context)

        uts = context['utdt_start'].strftime('%Y%b%d_%H%M')
        location = context['location']
        city = location.city.lower().replace(' ', '')
        loc = f'{city}{location.state.abbreviation}'

        # reportlab logic goes here
        buffer = io.BytesIO()
        p = canvas.Canvas(buffer, pagesize=letter) # width = 612, height = 792
        PAGE_WIDTH = defaultPageSize[0]
        PAGE_HEIGHT = defaultPageSize[1]

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
            reversed=False
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

        ######################################### PAGE 2
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

        ######################################### PAGE 4
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
            tel_view = create_planet_system_view(utdt, instance, cookie_dict['planets'], reversed=False)
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

        ######################################### PAGE 5
        # Asteroids
        FCX = [390, 30, 210, 390, 30, 210, 390, 30, 210, 390]
        FCY = [-45, 130, 130, 130, 310, 310, 310, 490, 490, 490]
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

        ######################################### PAGE 6
        # Comets
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


        # Moon
        y_start = y
        p.setFont('Helvetica-Bold', 14)
        p.drawString(50, y, 'Moon:')
        p.setFont('Helvetica', 10)
        y -= 15

        obs = cookie_dict['moon']['observe']
        ses = cookie_dict['moon']['session']
        app = cookie_dict['moon']['apparent']
        for s in [
            f"in {obs['constellation']['abbr']}",
            f"Phase: {obs['lunar_phase']['phase']}",
            f"Illum.: {obs['fraction_illuminated']:.1f}%",
            f"Dist.: {app['distance']['km']:.1f} km",
            f"Light Time: {to_time(app['distance']['light_time'])}",
            f"Mag: {obs['apparent_magnitude']:.2f}"
        ]:
            p, y = do_line(p, 50, y, s, dy=12)
        for alm in cookie_dict['moon']['almanac']:
            p.drawString(50, y, f"{alm['type']}: {isoparse(alm['ut']).strftime('%H:%M')} UT")
            y -= 12
        # Phase plot
        cookie_dict['moon']['name'] = 'Moon' # TODO: Fix this bug!
        moon_tel = create_planet_system_view(
            utdt,
            None,
            cookie_dict['moon'],
            object_type = 'moon',
            flipped = False,
            reversed = False
        )
        p.drawInlineImage(moon_tel, 390, y_start - 150, 180, 180)
        p.showPage()

        ######################################### PAGE 7
        # DSOs
        targets = []
        all_dsos = DSO.objects.filter(
            dec__gt=context['dec_limit'], 
            magnitude__lt=context['mag_limit'],
            priority__in=['Highest', 'High']
        ).order_by('constellation__abbreviation')
        
        for dso in all_dsos:
            if dso.object_is_up(location, context['utdt_start'], min_alt=20.) \
                    or dso.object_is_up(location, context['utdt_end'], min_alt=0.):
                #priority = dso.priority.lower()
                #if priority in targets.keys():
                #    targets[priority].append(dso)
                #else:
                #    targets[priority] = [dso]
                targets.append(dso)
        n_lines = 0
        dx = 0
        y = 720
        p.setFont('Helvetica-Bold', 14)
        p.drawString(50, y, 'DSOs:')
        p.setFont('Helvetica', 7)
        y -= 30
        dy = y
        # Test
        for dso in targets:
            p.roundRect(30+dx, y, 7, 7, 2, stroke=1, fill=0)
            if dso.priority == 'Highest':
                p.setFont('Helvetica-Bold', 7)
            p.drawString(45+dx, y, dso.shown_name)
            if dso.priority == 'Highest':
                p.setFont('Helvetica', 7)
            p.drawString(90+dx, y, dso.constellation.abbreviation)
            p.drawString(120+dx, y, dso.object_type.code)
            p.drawString(150+dx, y, f"{dso.magnitude:4.1f}")
            p.drawString(170+dx, y, f"{dso.number_of_observations:2d}")
            y -= 11
            n_lines += 1
            if n_lines % 50 == 0 and n_lines != 0:
                dx += 190
                y = dy
            if n_lines == 150:
                p.showPage()
                y = 720
                p.setFont('Helvetica-Bold', 14)
                p.drawString(50, y, 'DSOs (cont.):')
                p.setFont('Helvetica', 7)
                y = dy
                dx = 0
        p.showPage()

        ######################################### PAGE 8+
        # Observing Forms!
        n_form_pages = find_site_parameter('observe_form_pages', default=5, param_type='positive')

        
        for i in range(n_form_pages):
            y = 720
            p.setFont('Helvetica-Bold', 14)
            p.drawString(50, y, 'Observation Forms:')
            p.setFont('Helvetica-Bold', 12)
            y -= 20

            # Make some lines
            section_tops = [700, 500, 300, 100]
            for ly in section_tops:
                p.line(40, ly, PAGE_WIDTH-20, ly)

           
            for section in range(3):
                y = section_tops[section] - 20
                p.setFont('Helvetica-Bold', 12)
                ## Column 1: 
                for ll in [
                    'TIME: ____________________',
                    'OBJECT: __________________',
                    'OBJ TYPE: ________________',
                    'CONST: ___________________',
                    'EYEPS: ___________________',
                    'FILTERS: _________________',
                ]:
                    p, y = do_line(p, 50, y, ll, dy=22)


                ## Column 2:
                y = section_tops[section] - 20
                notes = ['NOTES: _________________'] + \
                    5 * ['________________________']
                for ll in notes:
                    p, y = do_line(p, 250, y, ll, dy=22)

                y -= 10
                p.setFont('Helvetica-Bold', 9)
                p, y = do_line(p,  50, y, 'SQM: __________', dy=0)
                p, y = do_line(p, 150, y, 'Temp: _________', dy=0)
                p, y = do_line(p, 250, y, 'RH%: __________', dy=0)
                p, y = do_line(p, 350, y, 'Wind: _________', dy=0)
                p, y = do_line(p, 450, y, 'Clouds: _______________', dy=20)
                p, y = do_line(p,  50, y, 'Seeing: _______', dy=0)
                p, y = do_line(p, 150, y, 'Notes: ____________________________________________________________________', dy=0)

            # Column 3:
            # Drawing circle
                p.circle(500, section_tops[section]-80, 72)

            p.showPage()

        ### FINISH IT
        p.save()
        buffer.seek(0)

        #filename = f'skytour_plan_{uts}_{loc}.pdf'

        response = HttpResponse(buffer, content_type='application/pdf')
        return response

