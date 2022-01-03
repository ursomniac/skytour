from datetime import datetime
from django.views.generic.base import TemplateView

class HomePageView(TemplateView):
    """
    TODO: come up with a reason to have a home page... :-)
    """
    template_name = 'home.html'
    
    def get_context_data(self, **kwargs):
        context = super(HomePageView, self).get_context_data(**kwargs)
        return context
