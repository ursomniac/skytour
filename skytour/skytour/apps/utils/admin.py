from django.contrib import admin
from .models import Catalog, Constellation, ObjectType, StarCatalog

class ConstellationNeighborInline(admin.TabularInline):
    model = Constellation.neighbors.through
    fk_name = 'from_constellation'
    extra = 0

class CatalogAdmin(admin.ModelAdmin):
    list_display = ['pk', 'name', 'abbreviation', 'lookup_mode', 'number_objects', 'precedence', 'expected_complete']

class StarCatalogAdmin(admin.ModelAdmin):
    list_display = ['pk', 'name', 'abbreviation', 'precedence']

class ConstellationAdmin(admin.ModelAdmin):
    list_display = [
        'pk', 'name', 'abbreviation', 
        'center_ra', 'center_dec', 'area'
    ]
    list_display_links = ['pk', 'name', 'abbreviation']
    search_fields = ['name', 'abbreviation']
    inlines = [ConstellationNeighborInline]
    fieldsets = (
        (None, {
            'fields': [
                ('name', 'abbreviation'), 
                ('genitive', 'translation'),
                ('center_ra', 'center_dec', 'area'),
                ('map', 'reverse_map'),
                ('other_map', 'reverse_other_map'),
                'historical_image',
                'description'
            ]
        }),
    )

class ObjectTypeAdmin(admin.ModelAdmin):
    model = ObjectType
    list_display = ['pk', 'name', 'slug',  'marker_type', 'map_symbol_type', 'marker_color']

admin.site.register(Catalog, CatalogAdmin)
admin.site.register(Constellation, ConstellationAdmin)
admin.site.register(ObjectType, ObjectTypeAdmin)
admin.site.register(StarCatalog, StarCatalogAdmin)