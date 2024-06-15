from django.views.generic.base import TemplateView
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
        return context

class AstroCalcDistanceView(TemplateView):
    template_name='astro_calc.html'

    def get_context_data(self, **kwargs):
        context = super(AstroCalcDistanceView, self).get_context_data(**kwargs)
        mod = self.request.GET.get('modulus')
        print("MOD: ", mod)
        print("HAZ: ", haz(mod))
        if not haz(mod):
            return context
        context['mly'] = get_distance_from_modulus(float(mod))
        context['modulus'] = float(mod)
        return context

class AstroCalcAngularSizeView(TemplateView):
    template_name='astro_calc.html'

    def get_context_data(self, **kwargs):
        context = super(AstroCalcAngularSizeView, self).get_context_data(**kwargs)
        d25 = self.request.GET.get('d25')
        r25 = self.request.GET.get('r25')
        print("IN Angsize")

        if not haz(r25) and not haz(d25):
            return context
        # have d25/r25 
        if haz(r25) and haz(d25):
            context['amajor'], context['aminor'] = get_size_from_logd25(float(r25), float(d25), raw=True)
            context['r25'] = float(r25)
            context['d25'] = float(d25)
        if haz(r25) and not haz(d25):
            context['amajor'], _ = get_size_from_logd25(float(r25), raw=True)
            context['r25'] = float(r25)
            context['d25'] = None
        return context

class AstroCalcSQMView(TemplateView):
    template_name='astro_calc.html'

    def get_context_data(self, **kwargs):
        context = super(AstroCalcSQMView, self).get_context_data(**kwargs)
        sqs = self.request.GET.get('sqs')
        sqm = self.request.GET.get('sqm')
        print("IN SQS")
        if not haz(sqs) and not haz(sqm):
            return context
        if haz(sqm) and not haz(sqs):
            context['sqs'] = sqm_to_sqs(float(sqm))
            context['sqm'] = float(sqm)
        elif haz(sqs) and not haz(sqm):
            context['sqm'] = sqs_to_sqm(float(sqs))
            context['sqs'] = float(sqs)
        else:
            context['sqm'] = sqs_to_sqm(float(sqs))
            context['sqs'] = float(sqs)
        return context
