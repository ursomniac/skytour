import io

from django.http import HttpResponse
from django.views.generic import View
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

from .cookie import deal_with_cookie, get_all_cookies
from .pdf_pages.dso import do_dso_long_list, do_dso_lists
from .pdf_pages.observing_form import do_observing_form
from .pdf_pages.page1 import do_page1
from .pdf_pages.solar_system import do_asteroids, do_comets, do_moon, do_planets
from .pdf_pages.stars import do_skymap, do_zenith
from .plan import get_plan


class PlanPDFView(View):
    def get_context_data(self, **kwargs):
        context = {}
        return context

    def get(self, request, *args, **kwargs):
        # Get plan parameters, objects
        context = self.get_context_data()
        context = deal_with_cookie(request, context)
        context['cookies'] = get_all_cookies(request)
        context = get_plan(context)
        # Create a PDF file
        buffer = io.BytesIO()
        p = canvas.Canvas(buffer, pagesize=letter)
        p = do_page1(p, context)         # Cover Page
        p = do_skymap(p, context)        # Skymap
        p = do_zenith(p, context)        # Zenith Chart
        p = do_planets(p, context)       # Planets
        p = do_asteroids(p, context)     # Asteroids
        p = do_comets(p, context)        # Comets
        p = do_moon(p, context)          # Moon   
        p = do_dso_lists(p, context)     # DSO Lists       
        p = do_dso_long_list(p, context) # Long list of DSOs
        p = do_observing_form(p, context)
        p.save()
        buffer.seek(0)
        response = HttpResponse(buffer, content_type='application/pdf')
        return response

