from django.contrib import admin
from ..abstract.admin import AbstractObservation, ObservableObjectAdmin
from .models import Planet, MeteorShower, Asteroid, Comet, PlanetObservation, CometObservation, AsteroidObservation

class AsteroidObservationAdmin(AbstractObservation):
    model = AsteroidObservation

class CometObservationAdmin(AbstractObservation):
    model = CometObservation

class PlanetObservationAdmin(AbstractObservation):
    model = PlanetObservation

class MeteorShowerAdmin(admin.ModelAdmin):
    model = MeteorShower
    list_display = ['pk', 'name', 'radiant_ra', 'radiant_dec', 'start_date', 'peak_date', 'end_date']
    fieldsets = (
        (None, {
            'fields': [
                ('name', 'slug'),
                ('start_date', 'peak_date', 'end_date'),
                ('radiant_ra', 'radiant_dec', 'longitude'),
                ('speed', 'zhr', 'parent_body'),
                'notes',
                'est_brightest'
            ]
        }),
    )

class PlanetAdmin(ObservableObjectAdmin):
    model = Planet
    list_display = [
        'pk', 'name', 'diameter', 'load', 'moon_list', 'n_obs', 'obs_date'
    ]
    list_display_links = ['pk', 'name']
    readonly_fields = ['moon_list',]
    inlines = [PlanetObservationAdmin]
    save_on_top = True

class AsteroidAdmin(ObservableObjectAdmin):
    model = Asteroid
    list_display = ['number', 'name', 'diameter', 'est_brightest', 'h', 'n_obs', 'obs_date']
    list_display_links = ['number', 'name']
    inlines = [AsteroidObservationAdmin]
    save_on_top = True

class CometAdmin(ObservableObjectAdmin):
    model = Comet
    list_display = ['pk', 'name', 'status', 'n_obs', 'obs_date']
    list_display_links = ['pk', 'name']
    inlines = [CometObservationAdmin]
    save_on_top = True
    
admin.site.register(MeteorShower, MeteorShowerAdmin)
admin.site.register(Planet, PlanetAdmin)
admin.site.register(Asteroid, AsteroidAdmin)
admin.site.register(Comet, CometAdmin)