import io

from django.http import HttpResponse
from django.views.generic import View
from django.views.generic.edit import FormView
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

from ..site_parameter.helpers import find_site_parameter
from ..session.utils import get_initial_from_cookie

from .cookie import deal_with_cookie, get_all_cookies
from .forms import CustomPlanPDFForm
from .plan import get_plan
from .pdf_pages.dso import do_dso_long_list
from .pdf_pages.observing_form import do_observing_form
from .pdf_pages.page1 import do_page1
from .pdf_pages.solar_system import do_asteroids, do_comets, do_moon, do_planets
from .pdf_pages.stars import do_skymap, do_zenith



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
        p = do_dso_long_list(p, context) # Long list of DSOs
        p = do_observing_form(p, context)
        p.save()
        buffer.seek(0)
        response = HttpResponse(buffer, content_type='application/pdf')
        return response

class CustomPlanPDFFormView(FormView):
    template_name = 'custom_pdf_form.html'
    form_class = CustomPlanPDFForm

    def get_initial(self):
        initial = super().get_initial() # needed since we override?
        initial = get_initial_from_cookie(self.request, initial)
        time_zone = find_site_parameter('default-time-zone-id', None, 'positive')
        if time_zone is not None:
            initial['time_zone'] = time_zone
        return initial

    def get_context_data(self, **kwargs):
        context = super(CustomPlanPDFFormView, self).get_context_data(**kwargs)
        context = deal_with_cookie(self.request, context)
        context['cookies'] = get_all_cookies(self.request)
        return context

    def form_valid(self, form, **kwargs):
        context = self.get_context_data(**kwargs)
        d = form.cleaned_data

        #return super().form_valid(form)
        return self.render_to_response(context)

    def post(self, request, *args, **kwargs):
        form = self.get_form(self.get_form_class())
        if form.is_valid():
            return self.form_valid(form, **kwargs)
        return self.form_invalid(form, **kwargs)

class CustomPlanPDFView(View):
    
    def get_context_data(self, **kwargs):
        context = super(CustomPlanPDFView, self).get_context_data.kwargs()
        print("CONTEXT: ", context)
        return context