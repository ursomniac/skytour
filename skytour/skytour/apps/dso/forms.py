from django import forms
from django.forms import inlineformset_factory
from .models import DSO, DSOObservation, DSOObservingMode
from ..abstract.vocabs import YES_NO, YES, NO

class DSOListCreateForm(forms.Form):
    name = forms.CharField (required=True)
    description = forms.CharField (required=False, widget=forms.TextInput())
    # dso has to be not required!
    active_observing_list = forms.ChoiceField (
        choices = YES_NO, initial=YES
    )

class DSOListEditForm(forms.Form):
    name = forms.CharField (required=True)
    description = forms.CharField (required=False, widget=forms.TextInput())
    # dso has to be not required!
    active_observing_list = forms.ChoiceField (
        choices = YES_NO, initial=YES
    )
    delete_checkbox = forms.BooleanField(
        required=False,
    )

class DSOMetadataForm(forms.ModelForm):

    class Meta:
        model = DSO
        fields = [
            'nickname',
            'reimage',
            'show_on_skymap',
            'show_on_simple_skymap',
            'override_metadata',

            'magnitude', 'magnitude_system',
            'angular_size', 'major_axis_size', 'minor_axis_size',
            'surface_brightness', 'orientation_angle',
            'distance', 'distance_units',
            'other_parameters',
            'notes'
        ]

class DSOObservationEditForm(forms.ModelForm):
    # TODO V2: Add delete button
    class Meta:
        model = DSOObservation
        fields = ['session', 'telescope', 'eyepieces', 'filters', 'ut_datetime', 'notes']

class DSOObservingModeForm(forms.ModelForm):
    class Meta:
        model = DSOObservingMode
        fields = ['mode', 'viable', 'priority', 'interesting', 'challenging', 'notes']

DSOModeFormSet = inlineformset_factory(
    DSO,
    DSOObservingMode,
    DSOObservingModeForm,
    extra = 0, # this has to be overridable somehow...
    can_delete = True # ugh - don't really want this... but...
)