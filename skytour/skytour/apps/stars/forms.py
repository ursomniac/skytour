from django import forms
from ..session.forms import GRAPH_COLOR_SCHEME

class ZenithMagForm(forms.Form):
    ut_date = forms.DateField(label="UT Date")
    ut_time = forms.TimeField(label="UT Time")
    mag_limit = forms.FloatField(initial=6.5)
    zenith_limit = forms.FloatField(
        initial=20.,
        help_text = 'Extent from zenith (degrees)'
    )
    color_scheme = forms.ChoiceField(choices=GRAPH_COLOR_SCHEME, initial='dark')
