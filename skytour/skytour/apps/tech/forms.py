from django import forms
from .models import Telescope  #Eyepiece, Sensor, Filter

class TelescopeForm(forms.ModelForm):

    class Meta:
        model = Telescope
        fields = [
            'name', 
            'aperture', 
            'focal_length', 
            'order_in_list', 
            'active', 
            'is_default'
        ]

class TelescopeDeleteForm(forms.Form):
    delete_confirm = forms.BooleanField(required=False)

    class Meta:
        fields = ['delete_confirm']