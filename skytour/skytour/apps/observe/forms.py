from django import forms
from django.forms import inlineformset_factory
from .models import ObservingLocation, ObservingLocationMask

class NewObservingLocationForm(forms.ModelForm):
    class Meta:
        model = ObservingLocation
        fields = [
            'status',
            'is_default',
            'name',
            'street_address',
            'city',
            'state',
            'region',
            'latitude',
            'longitude',
            'elevation',
            'time_zone',
            'travel_distance',
            'travel_time',
            'sqm',
            'brightness',
            'artificial_brightness',
            'ratio',
            'bortle',
            'parking',
            'is_flat',
            'description',
            'light_sources',
            'horizon_blockage',
            'map_image',
            'earth_image',
            'bortle_image',
        ]

class ObservingLocationMaskForm(forms.ModelForm):

    def __init__(self, *arg, **kwargs):
        super(ObservingLocationMaskForm, self).__init__(*arg, **kwargs)
        self.empty_permitted = True

    class Meta:
        model = ObservingLocationMask
        fields = ['azimuth_start', 'altitude_start', 'azimuth_end', 'altitude_end']

ObservingLocationUpdateMaskFormset = inlineformset_factory(
    ObservingLocation, 
    ObservingLocationMask,
    form = ObservingLocationMaskForm,
    fields = ['azimuth_start', 'altitude_start', 'azimuth_end', 'altitude_end'],
    extra = 2,
    can_delete = True
)
ObservingLocationAddMaskFormset = inlineformset_factory(
    ObservingLocation, 
    ObservingLocationMask,
    form = ObservingLocationMaskForm,
    fields = ['azimuth_start', 'altitude_start', 'azimuth_end', 'altitude_end'],
    extra = 8,
    can_delete = True
)

class ObservingLocationDeleteForm(forms.Form):
    delete_confirm = forms.BooleanField(required=False)

    class Meta:
        fields = ['delete_confirm']