from django.contrib import admin
from .models import Planet

class PlanetAdmin(admin.ModelAdmin):
    model = Planet
    list_display = [
        'pk', 'name', 'diameter', 'load', 'moon_list'
    ]
    list_display_links = ['pk', 'name']
    readonly_fields = ['moon_list',]

admin.site.register(Planet, PlanetAdmin)