import datetime, pytz
import io
from dateutil.parser import isoparse
from django.http import HttpResponse
from django.views.generic import View

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.rl_config import defaultPageSize
from ..observe.pdf import (
    bold_text, 
    add_image, 
    place_text
)
from ..observe.pdf import DEFAULT_BOLD, DEFAULT_FONT, DEFAULT_FONT_SIZE, DEFAULT_ITAL
from ..session.cookie import deal_with_cookie, get_all_cookies
from ..solar_system.plot import (
    create_planet_system_view, 
    create_finder_chart,
    get_planet_map
)
from .models import Asteroid, Comet, Planet

def get_rise_set(alist, format="%Y-%m-%d %I:%M %p"):
    orise = None
    oset = None

    for e in alist:
        tstr = isoparse(e['local_time']).strftime(format)
        if e['type'] == 'Rise':
            orise = tstr
        elif e['type'] == 'Set':
            oset = tstr
    return orise, oset


def get_object(object_type, object_id):
    model = {'asteroid': Asteroid, 'comet': Comet, 'planet': Planet}
    try:
        if object_type == 'comet':
            obj = Comet.objects.get(pk=int(object_id))
        else:
            obj = model[object_type].objects.get(slug=object_id)
        return obj
    except:
        print(f"Error getting {object_type} {object}")
        return None

def get_cookie_value(cookie, object_type, object):
    if object_type == 'asteroid':
        for a in cookie['asteroids']:
            if object.number == a['number']:
                return a
    elif object_type == 'comet':
        for c in cookie['comets']:
            if object.pk == c['pk']:
                return c
    elif object_type == 'planet':
        if object.name in cookie['planets'].keys():
            return cookie['planets'][object.name]
    return None

FS = 10
def create_pdf_view(p, utdt, object, object_type, session, cookies):
    """
    Unlike the others this creates a page on the fly
    based on the cookie settings.
    """
    PAGE_WIDTH = defaultPageSize[0]
    PAGE_HEIGHT = defaultPageSize[1]
    location = cookies['location']
    time_zone = pytz.timezone(cookies['time_zone']) if cookies['time_zone'] is not None else None

    app = session['apparent']
    obs = session['observe']
    phy = session['physical']

    X0 = 50
    y0 = 750

    # Title
    y = y0
    p, tw = bold_text(p, X0, y, object.name, size=20)
    # Metadata
    #   - Overall (UTDT, etc.)
    p, tw = bold_text(p, 300, y, 'Date: ', size=FS)
    tstr = cookies['utdt_start'].strftime('%Y-%m-%d %H:%M')
    lstr = cookies['utdt_start'].astimezone(time_zone).strftime("%Y-%m-%d %H:%M %z") if time_zone is not None else None
    p = place_text(p, 300 + tw, y, f"{lstr}  ({tstr} UT)", size=FS)

    y -= 15
    p, tw = bold_text(p, 300, y, "Loc: ", size=FS)
    p = place_text(p, 300 + tw, y, f'{location}', size=FS)
    y -= 15
    p, tw = bold_text(p, 300, y, "Lat: ", size=FS)
    p = place_text(p, 300 + tw, y, f"{location.latitude}", size=FS)
    y -= 15
    p, tw = bold_text(p, 300, y, "Long: ", size=FS)
    p = place_text(p, 300 + tw, y, f'{location.longitude}', size=FS)
    #   - Almanac (rise/set)
    y = y0 - 30
    orise, oset = get_rise_set(session['almanac'])
    p, tw = bold_text(p, X0, y, "Rise: ", size=FS)
    p = place_text(p, X0 + tw, y, orise, size=FS)
    y -= 15
    p, tw = bold_text(p, X0, y, 'Set: ', size=FS)
    p = place_text(p, X0 + tw, y, oset, size=FS)
    #   - Apparent/Astro 
    #       RA, Dec
    y -= 30
    ynow = y
    p, tw = bold_text(p, X0, y, u'RA: ', size=FS)
    p = place_text(p, X0 + tw, y, app['equ']['ra_str'], size=FS)
    y -= 15
    p, tw = bold_text(p, X0, y, u'Dec: ', size=FS)
    p = place_text(p, X0 + tw, y, app['equ']['dec_str'], size=FS)
    #       mag, ang size, etc.
    xnow = 200
    y = ynow
    p, tw = bold_text(p, xnow, y, 'Mag: ', size=FS)
    p = place_text(p, xnow + tw, y, f"{obs['apparent_magnitude']:.2f}", size=FS)
    p, tw = bold_text(p, xnow, y-15, 'Ang Diam: ', size=FS)
    p = place_text(p, xnow + tw, y-15, obs['angular_diameter_str'], size=FS)
    #       distance
    y = ynow
    xnow = 400
    p, tw = bold_text(p, xnow, y, 'Dist: ', size=FS)
    dist = app['distance']
    p = place_text(p, xnow + tw, y, f"{dist['au']:.2f} AU = {dist['mi']/1.e6:.1f} Mmi", size=FS)
    p = place_text(p, xnow + tw, y-15, f"{dist['light_time_str']}", size=FS)
    # Planets section
    y -= 30
    if object_type == 'planet':
        # % Illum
        # Elong.
        p, tw = bold_text(p, X0, y, '% Illum: ', size=FS)
        p = place_text(p, X0 + tw, y, f"{obs['fraction_illuminated']:.1f} %", size=FS)
        p, tw = bold_text(p, 200, y, 'Elong: ', size=FS)
        p = place_text(p, 200 + tw, y, f"{obs['elongation']:.2f}°", size=FS)

    # Finder Chart
    y -= 10
    finder, _ = create_finder_chart(
        utdt, 
        object, 
        planets_cookie=cookies['cookies']['planets'], 
        asteroids=cookies['cookies']['asteroids'], 
        object_type = object_type,
        obj_cookie = session,
        fov = 5,
        reversed=False
    )
    p, newy = add_image(p, y, finder, x=50, size=250)
    # Moon/Phase Chart
    if object_type == 'planet':
        telview = create_planet_system_view(
            utdt, 
            object, 
            cookies['cookies']['planets'], 
            reversed=False
        )
        p, newy = add_image(p, y, telview, x=300, size=250)
        y -= 250
        if object.slug not in ['mercury', 'venus']:
            p.setFont(DEFAULT_ITAL, 8)
            p.drawString(380, y, 'ID above + = moon behind planet')
            p.setFont(DEFAULT_FONT, DEFAULT_FONT_SIZE)
    # Map
    if object_type == 'planet' and object.slug in ['mars', 'jupiter']:
        y -= 20
        #p, tw = bold_text(p, X0, y, 'Physical')
        px, py, planet_map = get_planet_map(object, phy)
        aratio = object.planet_map.height / object.planet_map.width
        mapy = y + 250 * aratio 
        p, newy = add_image(p, mapy, planet_map, size=500)
        y = y - 500 * aratio - 20
        p, tw = bold_text(p, 80, y, 'Name', size=9)
        p, tw = bold_text(p, 220, y, 'Visibility', size=9)
        p, tw = bold_text(p, 270, y, 'T from Merid.', size=9)
        p, tw = bold_text(p, 370, y, 'at UT', size=9)
        y -= 10
        p.line(70, y, 530, y)
        y -= 10
        for f in phy['features']:
            p = place_text(p, 80, y, f['name'], size=8)
            p = place_text(p, 220, y, f['view'], size=8)
            p = place_text(p, 270, y, f"{f['time_from_meridian']:5.2f} hrs", size=8)
            tt = isoparse(f['next_transit']).strftime('%Y-%m-%d %H:%I')
            p = place_text(p, 370, y, f"{tt} UT", size=8)
            y -= 10

    p.showPage()
    return p

    
class SSOPDFView(View):

    def get_context_data(self, **kwargs):
        context = {}
        return context

    def get(self, request, *args, **kwargs):
        context = self.get_context_data()
        context = deal_with_cookie(request, context)
        utdt = context['utdt_start']
        context['cookies'] = get_all_cookies(request)
        object_type = kwargs.get('object_type', None)
        object_id = kwargs.get('object_id', None)
        object = get_object(object_type, object_id)
        session = get_cookie_value(context['cookies'], object_type, object)
        obj_rise, obj_set = get_rise_set(session['almanac'])
        #location = ObservingLocation.objects.get(pk=context['location'])
        if object:
            # Start file.
            buffer = io.BytesIO()
            p = canvas.Canvas('/tmp/foo.pdf', pagesize=letter)
            p = canvas.Canvas(buffer, pagesize=letter)
            p = create_pdf_view(p, utdt, object, object_type, session, context)
            p.save()
            buffer.seek(0)
            response = HttpResponse(buffer, content_type='application/pdf')
            return response
        else:
            # TODO: 404?
            pass