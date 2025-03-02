from django import forms
from .models import DSOList
from ..abstract.vocabs import YES_NO, YES, NO
from ..utils.models import ObjectType
from .vocabs import PRIORITY_CHOICES

class DSOFilterForm(forms.Form):
    ra_min = forms.FloatField(required=False)
    ra_max = forms.FloatField(required=False)
    dec_min = forms.FloatField(required=False)
    dec_max = forms.FloatField(required=False)
    mag_max = forms.FloatField(required=False)
    surface_max = forms.FloatField(required=False)
    object_type = forms.ModelMultipleChoiceField(
        required=False,
        widget=forms.CheckboxSelectMultiple(),
        queryset = ObjectType.objects.all(),
        initial = [c for c in ObjectType.objects.all().values_list("id", flat=True)]
    )
    priority = forms.MultipleChoiceField (
        required = False,
        widget = forms.CheckboxSelectMultiple,
        choices = PRIORITY_CHOICES,
        initial = [c for c in ('Highest', 'High', 'Medium')]
    )
    filter_imaged = forms.BooleanField (required=False)
    #catalog = forms.ModelMultipleChoiceField (
    #    required = False,
    #    widget = forms.CheckboxSelectMultiple(),
    #    queryset = Catalog.objects.all(),
    #    initial = [c for c in Catalog.objects.all().values_list("id", flat=True)]
    #)

class DSOAddForm(forms.ModelForm):
    add_dso = forms.ModelChoiceField(
        queryset=None,
        widget=forms.CheckboxSelectMultiple()
    )
    dso_list = forms.ModelChoiceField (
        queryset = DSOList.objects.all(),
        required = False
    )
    new_dso_list = forms.CharField (required=False)
    new_dso_description = forms.CharField (required=False, widget=forms.TextInput())

    def __init__(self, dso_subset, *args, **kwargs):
        super(DSOAddForm, self).__init__(*args, **kwargs)
        if dso_subset is not None:
            self.fields['add_dso'].queryset = dso_subset
        else:
            self.fields['add_dso'] = None

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