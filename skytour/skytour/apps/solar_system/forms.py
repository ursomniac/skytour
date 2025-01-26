import datetime
from django import forms
from matplotlib.pyplot import show
from ..session.cookie import deal_with_cookie
from .models import Asteroid, Planet, Comet
from .vocabs import STATUS_CHOICES, BACKGROUND_CHOICES

def date_plus_10():
    today = datetime.datetime.utcnow()
    return today + datetime.timedelta(days=10)

class TrackerForm(forms.Form):
    start_date = forms.DateField(
        initial=datetime.datetime.now
    )
    end_date = forms.DateField(
        initial=date_plus_10
    )
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
    #show_planets = forms.ChoiceField( 
    #    initial = 0, 
    #    choices = STATUS_CHOICES,
    #    label = 'Show (other) Planets'
    #)
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

