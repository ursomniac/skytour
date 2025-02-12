from django.views.generic import TemplateView
from .models import *
    
class SiteParameterListView(TemplateView):
    template_name = 'site_parameter_list.html'

    def get_context_data(self, **kwargs):
        context = super(SiteParameterListView, self).get_context_data(**kwargs)
        context['parameters'] = {
            'positive': SiteParameterPositiveInteger.objects.all(),
            'string': SiteParameterString.objects.all(),
            'number': SiteParameterNumber.objects.all(),
            'float': SiteParameterFloat.objects.all(),
            'link': SiteParameterLink.objects.all(),
            'image': SiteParameterImage.objects.all(),
            'pdf': SiteParameterPDFFile.objects.all()
        }
        return context