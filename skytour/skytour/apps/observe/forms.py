from django import forms
from .models import ObservingLocation

class NewObservingLocationForm(forms.ModelForm):
    class Meta:
        model = ObservingLocation
        fields = [
            'status',
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