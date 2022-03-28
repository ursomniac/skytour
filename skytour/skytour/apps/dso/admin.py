from django.contrib import admin
from admin_auto_filters.filters import AutocompleteFilter
from ..abstract.admin import AbstractObservation, ObservableObjectAdmin
from .models import DSO, DSOImage, DSOAlias, DSOObservation

class ConstellationFilter(AutocompleteFilter):
    title = 'Constellation'
    field_name = 'constellation'

class DSOImageAdmin(admin.StackedInline):
    model = DSOImage
    extra = 0

class DSOAliasAdmin(admin.TabularInline):
    model = DSOAlias
    extra = 0
    fields = ['catalog', 'id_in_catalog']

class DSOObservationAdmin(AbstractObservation):
    model = DSOObservation

class DSOAdmin(ObservableObjectAdmin):
    list_display = [
        'pk', 
        'shown_name', 
        'nickname',
        'object_type',
        'ra_text', 
        'dec_text', 
        'magnitude',
        'constellation_abbreviation',
        'maj_axis',
        'priority',
        'n_obs',
        'obs_date'
    ]
    list_display_links = ['pk', 'shown_name',]
    readonly_fields = [
        'field_view_tag', 
        'finder_chart_tag',
        'dso_finder_chart_tag',
    ]
    list_filter = ['priority', 'show_on_skymap', 'object_type', 'ra_h', ConstellationFilter]
    search_fields = ['nickname', 'shown_name', 'aliases__shown_name']
    fieldsets = (
        (None, {
            'fields': [
                ('catalog', 'id_in_catalog'),
                ('constellation', 'show_on_skymap'),
                'nickname',
                ('object_type', 'morphological_type', 'priority'),
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
                ('magnitude', 'angular_size', 'major_axis_size', 'minor_axis_size'), 
                ('distance', 'distance_units'),
                ('surface_brightness', 'contrast_index', 'orientation_angle'),
                'notes',
            ]
        }),
        ('Charts', {
            'fields': [
                ('field_view', 'field_view_tag'),
                ('dso_finder_chart', 'dso_finder_chart_tag'),
                ('finder_chart', 'finder_chart_tag'),
                'pdf_page'
            ]
        })
    )
    inlines = [DSOAliasAdmin, DSOImageAdmin, DSOObservationAdmin]
    save_on_top = True

    # This is because stupid properties don't have short_description
    def list_ra(self, obj):
        return obj.format_ra
    list_ra.short_description = 'R.A.'

    def list_dec(self, obj):
        return obj.format_dec
    list_dec.short_description = 'Dec.'

    @admin.display(description='Con.', ordering='constellation')
    def constellation_abbreviation(self, obj):
        return obj.constellation

    @admin.display(description='Maj. Axis', ordering='major_axis_size')
    def maj_axis(self, obj):
        return obj.major_axis_size

    #@admin.display(description='# Obs.')
    #def n_obs(self, obj):
    #    return obj.number_of_observations

    #@admin.display(description='Date')
    #def obs_date(self, obj):
    #    if obj.last_observed is not None:
    #        return obj.last_observed.strftime("%Y-%m-%d")
    #    return None
    
    def get_form(self, request, obj=None, **kwargs):
        """
        This just removes some of the widgets in the admin because you'll never
        add a new constellation, etc.
        """
        form = super(DSOAdmin, self).get_form(request, obj, **kwargs)
        field = form.base_fields['constellation']
        field.widget.can_add_related = False
        field.widget.can_change_related = False
        field.widget.can_delete_related = False
        field = form.base_fields['object_type']
        field.widget.can_delete_related = False
        return form

admin.site.register(DSO, DSOAdmin)
