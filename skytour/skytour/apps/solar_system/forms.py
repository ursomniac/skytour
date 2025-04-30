import datetime
from django import forms
from ..astro.time import utc_now
from .models import (
    Asteroid, Planet, Comet,
    AsteroidObservation, PlanetObservation, CometObservation
)
from .vocabs import STATUS_CHOICES, BACKGROUND_CHOICES


class TrackerForm(forms.Form):
    start_date = forms.DateField()
    end_date = forms.DateField()
    object = forms.ChoiceField(choices=[])
    date_step = forms.IntegerField(
        initial=1,
        help_text = 'How often should we plot a poiint?'
    )
    label_step = forms.IntegerField(
        initial=5,
        help_text = 'How often should be put a label?'
    )
    fov = forms.FloatField(
        required=False,
        help_text = 'FOV of the map, defaults to the size of the tracking arc.'
    )
    mag_limit = forms.FloatField(
        required=False,
        help_text = 'Faintest star shown.'
    )
    reversed = forms.ChoiceField (
        initial = 'bow',
        choices = BACKGROUND_CHOICES,
        label = 'Display'
    )
    show_dsos = forms.ChoiceField(
        initial = 0,
        choices = STATUS_CHOICES,
        label = 'Show DSOs'
    )

    def __init__(self, asteroid_list=None, *args, **kwargs):
        super(TrackerForm, self).__init__(*args, **kwargs)
        planets = Planet.objects.all()
        c = [('planet--'+p.slug, p.name) for p in planets]
        if asteroid_list and len(asteroid_list) > 0:
            asteroids = Asteroid.objects.filter(slug__in=asteroid_list)
        else:
            asteroids = Asteroid.objects.all()
        c += [('asteroid--'+a.slug, f"{a.number} {a.name}") for a in asteroids]
        comets = Comet.objects.filter(status=1)
        c += [('comet--'+ str(x.pk), x.name) for x in comets]
        self.fields['object'].choices = c

class AsteroidEditForm(forms.ModelForm):

    class Meta:
        model = Asteroid
        fields = [
            'diameter',
            'year_of_discovery',
            'image',
            'classification',
            'description',
            'always_include',
            'est_brightest'
        ]

class CometEditForm(forms.ModelForm):

    class Meta:
        model = Comet
        fields = [
            'status',
            'mag_offset',
            'light_curve_url',
            'light_curve_graph_url',
            'override_limits',
            #'perihelion_date'
        ]

class AsteroidObservationEditForm(forms.ModelForm):
    class Meta:
        model = AsteroidObservation
        fields = ['session', 'telescope', 'eyepieces', 'filters', 'ut_datetime', 'notes']

class CometObservationEditForm(forms.ModelForm):
    class Meta:
        model = CometObservation
        fields = ['session', 'telescope', 'eyepieces', 'filters', 'ut_datetime', 'notes']

class PlanetObservationEditForm(forms.ModelForm):
    class Meta:
        model = PlanetObservation
        fields = ['session', 'telescope', 'eyepieces', 'filters', 'ut_datetime', 'notes']

class CometManagementForm(forms.ModelForm):
    class Meta:
        model = Comet
        fields = ['name', 'status', 'mag_offset', 'override_limits',
                  'light_curve_url', 'light_curve_graph_url',
                ]
        
class AsteroidManagementForm(forms.ModelForm):
    class Meta:
        model = Asteroid
        fields = ['name', 'number',   # Needed
                  'diameter', 'year_of_discovery', 
                  'image', 'classification', 
                  'description', 'always_include']
