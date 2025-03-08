from django.utils.safestring import mark_safe
from django.views.generic.base import TemplateView
from ..observe.utils import get_effective_bortle
from .utils import get_distance_from_modulus, get_size_from_logd25, sqs_to_sqm

def haz(thing, zero=False):
    """
    Boolean against None | empty strings | strings == 'None'
    """
    if thing is None or thing.strip() == 'None' or len(thing.strip()) == 0:
        return False
    return True

class CalcModulusView(TemplateView):
    template_name = 'calc_value.html'

    def get_context_data(self, **kwargs):
        context = super(CalcModulusView, self).get_context_data()
        value = self.request.GET.get('value', None)
        context['title'] = 'Calculate Distance from Modulus'
        context['value_label'] = 'Dist. Modulus'
        context['submit_value'] = 'Convert to Mly'
        context['init_value'] = float(value) if value is not None else None

        if value is not None:
            if haz(value):
                result = get_distance_from_modulus(float(value))
                context['result_string'] = f"{result:.2f} Mly"
        return context
    
class CalcSQSToSQMView(TemplateView):
    template_name = 'calc_value.html'

    def get_context_data(self, **kwargs):
        context = super(CalcSQSToSQMView, self).get_context_data()
        value = self.request.GET.get('value', None)
        context['title'] = 'Calculate SQM from SQS'
        context['value_label'] = 'SQS'
        context['submit_value'] = 'Convert to SQM'
        context['init_value'] = float(value) if value is not None else None
        if value is not None:
            if haz(value):
                result = sqs_to_sqm(float(value))
                context['result_string'] = mark_safe(f"{result:.2f}<br>mag/arcmin<sup>2</sup>")
        return context
    
class CalcSQMToBortleView(TemplateView):
    template_name = 'calc_value.html'

    def get_context_data(self, **kwargs):
        context = super(CalcSQMToBortleView, self).get_context_data()
        value = self.request.GET.get('value', None)
        context['title'] = 'Calculate Bortle from SQM'
        context['value_label'] = 'SQM'
        context['submit_value'] = 'Convert to Bortle'
        context['value_type'] = 'number'
        context['init_value'] = float(value) if value is not None else None
        if value is not None:
            if haz(value):
                result = get_effective_bortle(float(value))
                context['result_string'] = mark_safe(f"Bortle {result:.2f}")
        return context
    
class CalcExposureFromFramesView(TemplateView):
    template_name = 'calc_frames.html'

    def get_context_data(self, **kwargs):
        context = super(CalcExposureFromFramesView, self).get_context_data()
        context['submit_value'] = 'Get Exposure Time'
        context['shutter_speed'] = [ 4, 10, 15, 20, 30 ]

        vframes = self.request.GET.get('frames', None)
        vexptime = self.request.GET.get('exptime', None)
        vcustom = self.request.GET.get('customexp', None)
        frames  = None if not haz(vframes)  else int(vframes)
        exptime = None if not haz(vexptime) else int(vexptime)
        custom  = None if not haz(vcustom)  else int(vcustom)

        # pick either exptime or custom depending
        not_exp = vexptime == "0" or vexptime is None
        factor = custom if not_exp else exptime
        if frames and factor:
            total_time = frames * factor
            time_min = int(total_time/60.)
            time_sec = int(total_time % 60)
            context['result_string'] = f"{time_min}m {time_sec:02d}s"
        context['frames'] = vframes
        context['exptime'] = vexptime
        context['customexp'] = vcustom
        return context
    
class CalcFramesFromExposureView(TemplateView):
    template_name = 'calc_times.html'

    def get_context_data(self, **kwargs):
        context = super(CalcFramesFromExposureView, self).get_context_data()
        context['submit_value'] = 'Get # Frames'
        context['shutter_speed'] = [ 4, 10, 15, 20, 30 ]

        vmin = self.request.GET.get('exp_min', 0)
        vsec = self.request.GET.get('exp_sec', 0)
        vexptime = self.request.GET.get('exptime', None)
        vcustom = self.request.GET.get('customexp', None)
        exptime = None if not haz(vexptime) else int(vexptime)
        custom  = None if not haz(vcustom)  else int(vcustom)

        total_time = int(vmin) * 60. + int(vsec)
        # pick either exptime or custom depending
        not_exp = vexptime == "0" or vexptime is None

        # pick either exptime or custom depending
        not_exp = vexptime == "0" or vexptime is None
        factor = custom if not_exp else exptime
        frames = None
        if total_time and factor:
            frames = int(0.5 + total_time / factor)
            context['result_string'] = f"{ frames }"
        context['frames'] = frames
        context['exp_min'] = vmin
        context['exp_sec'] = vsec
        context['exptime'] = vexptime
        context['customexp'] = vcustom
        return context
    
class CalcAngularSizeView(TemplateView):
    template_name = 'calc_angular.html'

    def get_context_data(self, **kwargs):
        context = super(CalcAngularSizeView, self).get_context_data()
        context['submit_value'] = 'Get Angular Size'
        vd25 = self.request.GET.get('d25', None)
        vr25 = self.request.GET.get('r25', None)

        d25 = None if not haz(vd25) else float(vd25)
        r25 = None if not haz(vr25) else float(vr25)
        context['d25'] = vd25
        context['r25'] = vr25

        if d25 and r25:
            angsize = get_size_from_logd25(d25, r25)
        elif d25 is not None and r25 is None:
            angsize = get_size_from_logd25(float(d25))
        else:
            angsize = None
        if angsize is not None:
            context['result_string'] = angsize
        return context