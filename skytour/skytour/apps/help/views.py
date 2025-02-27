from django.views.generic.base import TemplateView
from .vocabs import TEMPLATE_DICT

class HelpPopupView(TemplateView):
    """
    Make little popup pages for help/documentation
    """
    template_name = 'default_popup_help.html'
    
    def get_context_data(self, **kwargs):
        context = super(HelpPopupView, self).get_context_data(**kwargs)
        slug = self.kwargs['slug']
        if slug in TEMPLATE_DICT.keys():
            self.template_name = TEMPLATE_DICT[slug]
        return context

class HelpPageView(TemplateView):
    """
    General Help pages
    """
    template_name = 'main_help.html'

    def get_context_data(self, **kwargs):
        context = super(HelpPageView, self).get_context_data(**kwargs)
        slug = 'main-help' if 'slug' not in self.kwargs.keys() else self.kwargs['slug']
        if slug in TEMPLATE_DICT.keys(): # defaults to main help page
            self.template_name = TEMPLATE_DICT[slug]
        return context
