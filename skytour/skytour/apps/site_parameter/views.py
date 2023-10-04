from django.views.generic.list import ListView
from .models import SiteParameterLink

class SiteParameterLinkList(ListView):
    model = SiteParameterLink
    template_name = 'site_parameter_link_list.html'

    def get_context_data(self, **kwargs):
        context = super(SiteParameterLinkList, self).get_context_data(**kwargs)
        return context