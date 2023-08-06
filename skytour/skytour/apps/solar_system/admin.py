from django.contrib import admin
from ..abstract.admin import AbstractObservation, ObservableObjectAdmin
from .models import (
    Asteroid, AsteroidLibraryImage, AsteroidObservation,
    Comet, CometObservation, CometLibraryImage,
    Planet, PlanetLibraryImage, PlanetObservation, PlanetMoon,
    MoonObservation,
    MeteorShower, 
)

class AsteroidObservationAdmin(AbstractObservation):
    model = AsteroidObservation

class AsteroidLibraryImageAdmin(admin.StackedInline):
    model = AsteroidLibraryImage
    extra = 0
    readonly_fields = ['object_image_tag']
    fieldsets =  (
        (None, {
            'fields': [
                ('order_in_list', 'exposure', 'ut_datetime'),
                ('image', 'object_image_tag'),
                'notes'
            ]
        }),
    )

class CometObservationAdmin(AbstractObservation):
    model = CometObservation

class CometLibraryImageAdmin(admin.StackedInline):
    model = CometLibraryImage
    extra = 0
    readonly_fields = ['object_image_tag']
    fieldsets =  (
        (None, {
            'fields': [
                ('order_in_list', 'exposure', 'ut_datetime'),
                ('image', 'object_image_tag'),
                'notes'
            ]
        }),
    )

class PlanetObservationAdmin(AbstractObservation):
    model = PlanetObservation

class PlanetLibraryImageAdmin(admin.StackedInline):
    model = PlanetLibraryImage
    extra = 0
    readonly_fields = ['object_image_tag']
    fieldsets =  (
        (None, {
            'fields': [
                ('order_in_list', 'exposure', 'ut_datetime'),
                ('image', 'object_image_tag'),
                'notes'
            ]
        }),
    )
#class MoonObservationAdmin(AbstractObservation):
#    model = MoonObservation

class MeteorShowerAdmin(admin.ModelAdmin):
    model = MeteorShower
    list_display = ['pk', 'slug', 'name', 'intensity', 'radiant_ra', 'radiant_dec', 'start_date', 'peak_date', 'end_date', 'zhr']
    search_fields = ['name']
    fieldsets = (
        (None, {
            'fields': [
                ('name', 'slug', 'intensity'),
                ('start_date', 'peak_date', 'end_date'),
                ('radiant_ra', 'radiant_dec', 'longitude'),
                ('speed', 'zhr', 'parent_body'),
                'notes',
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
    inlines = [PlanetLibraryImageAdmin, PlanetObservationAdmin]
    save_on_top = True

class AsteroidAdmin(ObservableObjectAdmin):
    model = Asteroid
    list_display = ['number', 'name', 'diameter', 'est_brightest', 'h', 'n_obs', 'obs_date']
    list_display_links = ['number', 'name']
    inlines = [AsteroidLibraryImageAdmin, AsteroidObservationAdmin]
    save_on_top = True

class CometAdmin(ObservableObjectAdmin):
    model = Comet
    list_display = ['pk', 'name','peri_date', 'status', 'n_obs', 'obs_date']
    list_display_links = ['pk', 'name']
    inlines = [CometLibraryImageAdmin, CometObservationAdmin]
    save_on_top = True

    def peri_date(self, obj):
        return obj.perihelion_date

class PlanetMoonAdmin(admin.ModelAdmin):
    model = PlanetMoon
    list_display = ['pk', 'name', 'planet', 'planet_index', 'radius', 'major_axis', 'h', 'period_in_days', 'use_in_modeling']

admin.site.register(MeteorShower, MeteorShowerAdmin)
admin.site.register(Planet, PlanetAdmin)
admin.site.register(PlanetMoon, PlanetMoonAdmin)
admin.site.register(Asteroid, AsteroidAdmin)
admin.site.register(Comet, CometAdmin)
admin.site.register(MoonObservation)
#admin.site.register(PlanetObservation, PlanetObservationAdmin)
#admin.site.register(CometObservation, CometObservationAdmin)
#admin.site.register(AsteroidObservation, AsteroidObservationAdmin)