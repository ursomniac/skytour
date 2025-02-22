from django.views.generic.base import TemplateView
from .vocabs import TEMPLATE_DICT

class HelpPopupView(TemplateView):
    """
    Make little popup pages for help/documentation
    """
    template_name = 'default_help.html'
    
    def get_context_data(self, **kwargs):
        context = super(HelpPopupView, self).get_context_data(**kwargs)
        slug = self.kwargs['slug']
        if slug in TEMPLATE_DICT.keys():
            self.template_name = TEMPLATE_DICT[slug]
        return context

    