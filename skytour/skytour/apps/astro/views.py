from django.views.generic.base import TemplateView
from ..observe.utils import get_effective_bortle
from .utils import get_distance_from_modulus, get_size_from_logd25, sqs_to_sqm, sqm_to_sqs

def haz(thing):
    if thing is None or thing == 'None' or len(thing.strip()) == 0:
        return False
    return True

class AstroCalcView(TemplateView):
    template_name='astro_calc.html'

    def get_context_data(self, **kwargs):
        context = super(AstroCalcView, self).get_context_data(**kwargs)

        ctype = self.request.GET.get('calc')
        print(f"CTYPE: {ctype}")
        context['ctype'] = ctype

        if ctype == 'distance':
            modulus = self.request.GET.get('modulus')
            if haz(modulus):
                context['mly'] = get_distance_from_modulus(float(modulus))
                context['modulus'] = float(modulus)
        elif ctype == 'sqs':
            sqs = self.request.GET.get('sqs')
            if haz(sqs):
                context['sqm'] = sqs_to_sqm(float(sqs))
                context['sqs'] = float(sqs)
        elif ctype == 'angsize':
            d25 = self.request.GET.get('d25')
            r25 = self.request.GET.get('r25')
            if haz(d25):
                context['d25'] = float(d25)
                if haz(r25):
                    context['angsize'] = get_size_from_logd25(float(d25), float(r25))
                    context['r25'] = r25
                else:
                    context['angsize'] = get_size_from_logd25(float(d25))
        elif ctype == 'bortle':
            bsqm = self.request.GET.get('bsqm')
            if haz(bsqm):
                context['ebortle'] = get_effective_bortle(float(bsqm))
                context['bsqm'] = float(bsqm)
        return context

