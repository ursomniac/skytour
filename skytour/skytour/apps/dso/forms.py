from django import forms
from .models import DSOList, DSO
from ..abstract.vocabs import YES_NO, YES, NO
from ..utils.models import ObjectType
from .vocabs import PRIORITY_CHOICES, DISTANCE_UNIT_CHOICES

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

class DSOMetadataForm(forms.ModelForm):

    class Meta:
        model = DSO
        fields = [
            'nickname',
            'reimage',
            'override_metadata',

            'magnitude', 'magnitude_system',
            'angular_size', 'major_axis_size', 'minor_axis_size',
            'surface_brightness', 'orientation_angle',
            'distance', 'distance_units',
            'other_parameters',
            'notes'
        ]
    """
    nickname = forms.CharField(required=False)
    reimage = forms.BooleanField(
        label='Re-Image',
        required=False,
        help_text='Set the "REDO" flag to tag objects to re-image/observe'
    )
    override_metadata = forms.BooleanField(
        required=False,
        help_text='Show these values instead of SIMBAD/Hyperleda values'
    )

    # Metadata
    magnitude = forms.FloatField (required=False)
    magnitude_system = forms.CharField (
        label='Mag. System',
        required=False,
        help_text = 'e.g., V, B, Phot.'
    )
    angular_size = forms.CharField (
        label = 'Ang. Size',
        required=False,
        help_text = 'single or double dimension, e.g., 36\" or  8\'x5\''
    )
    major_axis_size = forms.FloatField (
        label = 'Major Axis',
        required = False,
        help_text = 'arcmin'
    )
    minor_axis_size = forms.FloatField (
        label = 'Minor Axis',
        required = False,
        help_text = 'arcmin'
    )
    surface_brightness = forms.FloatField (
        label = 'Surf. Brightness',
        required=False,
        help_text = 'Mag/arcmin^2 (SQM)'
    )
    # From Stellarium DSO model and SIMBAD
    orientation_angle = forms.IntegerField (
        label = 'Orientation Angle',
        required = False,
        min_value = 0,
        max_value = 180,
        help_text = 'Degrees'
    )
    #contrast_index = forms.FloatField (required=False)
    distance = forms.FloatField (required=False)
    distance_units = forms.ChoiceField (
        label = 'Dist. Units',
        required=False,
        choices = DISTANCE_UNIT_CHOICES
    )
    other_parameters = forms.CharField (
        required=False,
        widget=forms.TextInput,
        help_text = "Age, etc., in x: y; format - see README"
    )
    notes = forms.CharField (
        required=False,
        widget=forms.TextInput
    )
    """
