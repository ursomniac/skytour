from django.contrib import admin
from .models import Planet, MeteorShower, Asteroid, Comet, PlanetObservation, CometObservation, AsteroidObservation

class AsteroidObservationAdmin(admin.StackedInline):
    model = AsteroidObservation
    extra = 0
    fieldsets = (
        (None, {
            'fields': [
                ('ut_date', 'ut_time'),
                'notes'
            ]
        }),
    )
class CometObservationAdmin(admin.StackedInline):
    model = CometObservation
    extra = 0
    fieldsets = (
        (None, {
            'fields': [
                ('ut_date', 'ut_time'),
                'notes'
            ]
        }),
    )
class PlanetObservationAdmin(admin.StackedInline):
    model = PlanetObservation
    extra = 0
    fieldsets = (
        (None, {
            'fields': [
                ('ut_date', 'ut_time'),
                'notes'
            ]
        }),
    )

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

class PlanetAdmin(admin.ModelAdmin):
    model = Planet
    list_display = [
        'pk', 'name', 'diameter', 'load', 'moon_list'
    ]
    list_display_links = ['pk', 'name']
    readonly_fields = ['moon_list',]
    inlines = [PlanetObservationAdmin]
    save_on_top = True

class AsteroidAdmin(admin.ModelAdmin):
    model = Asteroid
    list_display = ['number', 'name', 'diameter', 'est_brightest', 'h']
    list_display_links = ['number', 'name']
    inlines = [AsteroidObservationAdmin]
    save_on_top = True

class CometAdmin(admin.ModelAdmin):
    model = Comet
    list_display = ['pk', 'name', 'status']
    list_display_links = ['pk', 'name']
    inlines = [CometObservationAdmin]
    save_on_top = True
    
admin.site.register(MeteorShower, MeteorShowerAdmin)
admin.site.register(Planet, PlanetAdmin)
admin.site.register(Asteroid, AsteroidAdmin)
admin.site.register(Comet, CometAdmin)