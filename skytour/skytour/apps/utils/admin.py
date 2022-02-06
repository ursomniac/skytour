from django.contrib import admin
from .models import Catalog, Constellation, ObjectType

class ConstellationNeighborInline(admin.TabularInline):
    model = Constellation.neighbors.through
    fk_name = 'from_constellation'
    extra = 0

class CatalogAdmin(admin.ModelAdmin):
    list_display = ['pk', 'name', 'abbreviation']

class ConstellationAdmin(admin.ModelAdmin):
    list_display = ['pk', 'name', 'abbreviation']
    list_display_links = ['pk', 'name', 'abbreviation']
    search_fields = ['name', 'abbreviation']
    inlines = [ConstellationNeighborInline]
    fieldsets = (
        (None, {
            'fields': [
                ('name', 'abbreviation', 'genitive'),
                ('map', 'other_map', 'historical_image'),
                'background',
            ]
        }),
    )

class ObjectTypeAdmin(admin.ModelAdmin):
    model = ObjectType
    list_display = ['pk', 'name', 'marker_type', 'map_symbol_type', 'marker_color']

admin.site.register(Catalog, CatalogAdmin)
admin.site.register(Constellation, ConstellationAdmin)
admin.site.register(ObjectType, ObjectTypeAdmin)