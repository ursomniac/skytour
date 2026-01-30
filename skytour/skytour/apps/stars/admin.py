from django.contrib import admin
from .models import BrightStar, DoubleStar, DoubleStarAlias, DoubleStarElements, VariableStar,\
    VariableStarTypeOriginal, VariableStarTypeRevised, ObservableVariableStar, VariableStarLightCurve,\
    StellarObject, BrightStarMetadata, BrightStarWiki, StellarObjectMetadata, StellarObjectWiki,\
    BrightStarNotes, AnnalsDeepSkyStar

class BrightStarMetadataInline(admin.StackedInline):
    model = BrightStarMetadata

class BrightStarWikiInline(admin.StackedInline):
    model = BrightStarWiki

class BrightStarNotesInline(admin.StackedInline):
    model = BrightStarNotes

class StellarObjectMetadataInline(admin.StackedInline):
    model = StellarObjectMetadata

class StellarObjectWikiInline(admin.StackedInline):
    model = StellarObjectWiki

class BrightStarAdmin(admin.ModelAdmin):
    model = BrightStar
    list_filter = ['constellation']
    list_display = ['pk', 'name', 'proper_name', 'hd_id']
    inlines = [BrightStarNotesInline, BrightStarMetadataInline, BrightStarWikiInline]
    search_fields = ('name', 'hd_id', 'hr_id', 'var_id')
    readonly_fields = ['hd_id', 'hr_id', 'sao_id', 'ra_text', 'dec_text', 'constellation', 'name']

    fieldsets = (
        (None, {
            'fields': [
                ('name', 'proper_name'),
                ('hr_id', 'hd_id', 'sao_id'),
                ('ra_text', 'dec_text', 'constellation'),
                'tags'
            ]
        }),
    )
    
class StellarObjectAdmin(admin.ModelAdmin):
    model = StellarObject
    list_filter = ['constellation']
    list_display = ['pk', 'shown_name','name', 'ra_text', 'dec_text', 'constellation', 'magnitude', 'spectral_type']
    search_fields = ('name',)
    # Aliases
    inlines = [StellarObjectMetadataInline, StellarObjectWikiInline]

    fieldsets = (
        (None, {
            'fields': [
                ('catalog', 'id_in_catalog', 'constellation'),
                'proper_name'
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
                ('magnitude', 'spectral_type'),
                'distance',
                'other_parameters',
                'notes',
                'tags'
            ]
        })
    )

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
                'tags',
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
    search_fields = ['name', 'id_in_catalog']
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

class AnnalsDeepSkyStarAdmin(admin.ModelAdmin):
    model = AnnalsDeepSkyStar
    list_display = ['pk', 'volume', 'page', 'constellation', 'flags_str', 'refs']
    autocomplete_fields = ('bright_star','variable_star', 'other_star')
    list_select_related = True
    fieldsets = (
        (None, {
            'fields': [
                ('volume', 'page', 'other_ref'),
                'bright_star',
                'variable_star', 
                'other_star',
                'byline',
                'notes',
                'metadata', 
            ]
        }),
    )

admin.site.register(BrightStar, BrightStarAdmin)
admin.site.register(DoubleStar, DoubleStarAdmin)
admin.site.register(StellarObject, StellarObjectAdmin)
admin.site.register(VariableStar, VariableStarAdmin)
admin.site.register(VariableStarTypeOriginal, VariableStarTypeOriginalAdmin)
admin.site.register(VariableStarTypeRevised)
admin.site.register(AnnalsDeepSkyStar, AnnalsDeepSkyStarAdmin)