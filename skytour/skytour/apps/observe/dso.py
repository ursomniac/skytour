from skyfield.api import JulianDate 
from ..skyobject.models import DSO

def assemble_dso_list(context=None):

    dsos = DSO.objects.all()
    if context['mag_limit']:
        dsos.exclude(magnitude__gt=context['magnitude'])
    if context['dec_limit']:
        dsos.exclude(dec__lt=context['dec_limit'])

