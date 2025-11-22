from django.contrib import admin
from .models import BrightStar, DoubleStar, DoubleStarAlias, DoubleStarElements, VariableStar,\
    VariableStarTypeOriginal, VariableStarTypeRevised, ObservableVariableStar, VariableStarLightCurve

class BrightStarAdmin(admin.ModelAdmin):
    model = BrightStar
    list_filter = ['constellation']

class DoubleStarElementsAdmin(admin.TabularInline):
    model = DoubleStarElements

class DoubleStarAliasAdmin(admin.TabularInline):
    model = DoubleStarAlias
    extra = 0
    fields = ['catalog', 'id_in_catalog']

class DoubleStarAdmin(admin.ModelAdmin):
    model = DoubleStar
    list_display = [
        'pk',
        'shown_name',
        'ra_text', 
        'dec_text',
        'magnitudes',
        'separation',
        'constellation_abbreviation',
    ]
    list_display_links = ['pk', 'shown_name']
    search_fields = ['shown_name', 'aliases__shown_name']
    inlines = [DoubleStarAliasAdmin, DoubleStarElementsAdmin]
    fieldsets = (
        (None, {
            'fields': [
                ('catalog', 'id_in_catalog', 'constellation'),
            ]
        }),
        ('Coordinates', {
            'fields': [
                ('ra_h', 'ra_m', 'ra_s'),
                ('dec_sign', 'dec_d', 'dec_m', 'dec_s')
            ]
        }),
        ('Attributes', {
            'fields': [
                ('magnitudes', 'spectral_type'),
                ('separation', 'distance'),
                'notes'
            ]
        })
    )
    save_on_top = True

    def list_ra(self, obj):
        return obj.format_ra
    list_ra.short_description = 'R.A.'

    def list_dec(self, obj):
        return obj.format_dec
    list_dec.short_description = 'Dec.'

    @admin.display(description='Con.', ordering='constellation')
    def constellation_abbreviation(self, obj):
        return obj.constellation

class VariableStarLightCurveAdmin(admin.TabularInline):
    model = VariableStarLightCurve
    extra = 0
    fields = ['order_by', 'image_file', 'date_start', 'date_end']

class VariableStarAdmin(admin.ModelAdmin):
    model = VariableStar

    list_display = [
        'pk',
        'id_in_catalog',
        'name',
        'list_ra', 
        'list_dec',
        'type_original',
        'constellation',
    ]
    list_filter = ['constellation', 'type_original']
    list_display_links = ['pk', 'name']
    search_fields = ['name']
    inlines = [VariableStarLightCurveAdmin]

    @admin.display(description='Con.', ordering='constellation')
    def constellation_abbreviation(self, obj):
        return obj.constellation

    def list_ra(self, obj):
        return obj.format_ra
    list_ra.short_description = 'R.A.'

    def list_dec(self, obj):
        return obj.format_dec
    list_dec.short_description = 'Dec.'

class VariableStarTypeOriginalAdmin(admin.ModelAdmin):
    model = VariableStarTypeOriginal
    list_display = ['pk', 'code', 'type_class', 'name', 'short_description']
    list_filter = ['type_class']
    ordering = ['pk', 'code', 'name']
    

class VariableStarTypeRevisedAdmin(admin.ModelAdmin):
    model = VariableStarTypeRevised
    list_display = ['pk', 'code', 'type_class', 'name', 'short_description']
    list_filter = ['type_class']
    ordering = ['pk', 'code', 'name']


admin.site.register(BrightStar, BrightStarAdmin)
admin.site.register(DoubleStar, DoubleStarAdmin)
admin.site.register(VariableStar, VariableStarAdmin)
admin.site.register(VariableStarTypeOriginal, VariableStarTypeOriginalAdmin)
admin.site.register(VariableStarTypeRevised)
