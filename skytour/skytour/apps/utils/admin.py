from django.contrib import admin
from .models import Catalog, Constellation, ObjectType

class CatalogAdmin(admin.ModelAdmin):
    list_display = ['pk', 'name', 'abbreviation']

class ConstellationAdmin(admin.ModelAdmin):
    list_display = ['pk', 'name', 'abbreviation']
    list_display_links = ['pk', 'name', 'abbreviation']
    search_fields = ['name', 'abbreviation']

admin.site.register(Catalog, CatalogAdmin)
admin.site.register(Constellation, ConstellationAdmin)
admin.site.register(ObjectType)