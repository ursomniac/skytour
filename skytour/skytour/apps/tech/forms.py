from django import forms
from .models import Telescope, Eyepiece, Filter

class TelescopeForm(forms.ModelForm):

    class Meta:
        model = Telescope
        fields = [
            'name', 
            'aperture', 
            'focal_length', 
            'order_in_list', 
            'active', 
            'is_default',
            'uses_eyepiece',
            'include_on_finder',
            'stellarium_telescope',
            'stellarium_sensor'
        ]

class TelescopeDeleteForm(forms.Form):
    delete_confirm = forms.BooleanField(required=False)

    class Meta:
        fields = ['delete_confirm']

class EyepieceForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super (EyepieceForm, self ).__init__(*args, **kwargs) # populates the post
        telescopes = Telescope.objects.filter(uses_eyepiece=True)
        self.fields['telescope'].queryset = telescopes
        print("Telescopes: ", telescopes)

    class Meta:
        model = Eyepiece
        fields = ['type', 'focal_length', 'apparent_fov', 'short_name', 'telescope']
        
class EyepieceDeleteForm(forms.Form):
    delete_confirm = forms.BooleanField(required=False)

    class Meta:
        fields = ['delete_confirm']

class EyepieceFilterForm(forms.ModelForm):

    class Meta:
        model = Filter
        fields = [
            'name', 'short_name', 'filter_type', 
            'central_wavelength', 'fwhm', 'dominant_wavelength',
            'transmission', 
            'transmission_curve', 'watten_curve',
            'notes', 'tech_notes'
        ]

class EyepieceFilterDeleteForm(forms.Form):
    delete_confirm = forms.BooleanField(required=False)

    class Meta:
        fields = ['delete_confirm']