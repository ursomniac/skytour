from ..solar_system.pdf import create_pdf_view
from .pdf_pages.dso import do_dso_lists
from .pdf_pages.observing_form import do_observing_form
from .pdf_pages.page1 import do_page1
from .pdf_pages.solar_system import do_asteroids, do_comets, do_moon, do_planets
from .pdf_pages.stars import do_skymap, do_zenith

def run_pdf(
        p, 
        context, 
        planet_list=None, 
        asteroid_list=None,
        comet_list=None,
        dso_lists=None, 
        skip=[], 
        pages=None
    ):
    utdt = context['utdt_start']
    planet_cookie = context['cookies']['planets']
    p = do_page1(p, context)             # Cover Page
    if 'skymap' not in skip:
        p = do_skymap(p, context)        # Skymap
    if 'zenith' not in skip:
        p = do_zenith(p, context)        # Zenith Chart
    if planet_list.count() > 0:     #planets' not in skip:
        p = do_planets(p, context)       # Planets Overview
    for planet in planet_list:
        pname = planet.name
        session = planet_cookie[pname]
        p = create_pdf_view(             # Individual Planets
            p, 
            utdt, 
            planet, 
            'planet', 
            session, 
            context
    )
    if asteroid_list.count() > 0:       # 'asteroids' not in skip:
        p = do_asteroids(p, context, asteroid_list=asteroid_list)     # Asteroids
    if comet_list.count() > 0:          # 'comets' not in skip:
        p = do_comets(p, context, comet_list=comet_list)        # Comets
    #if 'moon' not in skip:
    #    p = do_moon(p, context)          # Moon   
    if dso_lists is not None and dso_lists.count() > 0:
        p = do_dso_lists(p, context, dso_lists=dso_lists)     # DSO Lists       
    if 'forms' not in skip:
        p = do_observing_form(           # Blank Observing Forms
            p, 
            context, 
            pages=pages
    )
    p.save()
    return p
