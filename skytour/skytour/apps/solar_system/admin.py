from django.contrib import admin
from .models import Planet, MeteorShower, Asteroid

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
                'notes'
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

admin.site.register(MeteorShower, MeteorShowerAdmin)
admin.site.register(Planet, PlanetAdmin)
admin.site.register(Asteroid)
