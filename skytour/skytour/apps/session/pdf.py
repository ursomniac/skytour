from ..solar_system.pdf import create_pdf_view
from .pdf_pages.dso import do_dso_long_list, do_dso_lists
from .pdf_pages.observing_form import do_observing_form
from .pdf_pages.page1 import do_page1
from .pdf_pages.solar_system import do_asteroids, do_comets, do_moon, do_planets
from .pdf_pages.stars import do_skymap, do_zenith

def run_pdf(p, context, planet_list= None, skip=[], pages=None):
    utdt = context['utdt_start']
    planet_cookie = context['cookies']['planets']
    
    p = do_page1(p, context)             # Cover Page
    if 'skymap' not in skip:
        p = do_skymap(p, context)        # Skymap
    if 'zenith' not in skip:
        p = do_zenith(p, context)        # Zenith Chart
    if 'planets' not in skip:
        p = do_planets(p, context)       # Planets
    for planet in planet_list:
        pname = planet.name
        session = planet_cookie[pname]
        p = create_pdf_view(p, utdt, planet, 'planet', session, context)
    if 'asteroids' not in skip:
        p = do_asteroids(p, context)     # Asteroids
    if 'comets' not in skip:
        p = do_comets(p, context)        # Comets
    if 'moon' not in skip:
        p = do_moon(p, context)          # Moon   
    if 'dso_lists' not in skip:
        p = do_dso_lists(p, context)     # DSO Lists       
    if 'dsos' not in skip:
        p = do_dso_long_list(p, context) # Long list of DSOs
    if 'forms' not in skip:
        p = do_observing_form(p, context, pages=pages)
    p.save()
    return p
