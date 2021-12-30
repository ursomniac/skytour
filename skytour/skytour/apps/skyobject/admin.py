from django.contrib import admin
from admin_auto_filters.filters import AutocompleteFilter
from .models import DSO, DSOImage, DSOAlias, DSOObservation

class ConstellationFilter(AutocompleteFilter):
    title = 'Constellation'
    field_name = 'constellation'

class DSOImageAdmin(admin.StackedInline):
    model = DSOImage
    extra = 1
    readonly_fields = ['object_image_tag']
    fieldsets = (
        (None, {
            'fields': [
                ('image', 'object_image_tag'), 
                ('amateur_image', 'order_in_list'),
                'notes'
            ]
        }),
    )

class DSOAliasAdmin(admin.TabularInline):
    model = DSOAlias
    extra = 0
    fields = ['catalog', 'id_in_catalog']

class DSOObservationAdmin(admin.StackedInline):
    model = DSOObservation
    extra = 0
    fieldsets = (
        (None, {
            'fields': [
                ('ut_date', 'ut_time'),
                'notes'
            ]
        }),
    )

class DSOAdmin(admin.ModelAdmin):
    list_display = [
        'pk', 
        'shown_name', 
        'nickname',
        'object_type',
        'ra_text', 
        'dec_text', 
        'magnitude',
        'constellation',
        'priority',
        #'has_observations'
    ]
    list_display_links = ['pk', 'shown_name',]
    readonly_fields = [
        'field_view_tag', 
        'finder_chart_tag',
        'dso_finder_chart_tag',
    ]
    list_filter = ['priority', 'object_type', 'ra_h', ConstellationFilter]
    #list_filter = ['object_type', 'ra_h', 'constellation']
    search_fields = ['nickname', 'shown_name', 'aliases__shown_name']
    fieldsets = (
        (None, {
            'fields': [
                ('catalog', 'id_in_catalog'),
                'constellation',
                'nickname',
                ('object_type', 'priority'),
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
                ('magnitude', 'angular_size'), 
                ('distance', 'distance_units'),
                ('surface_brightness', 'contrast_index'),
                'notes',
            ]
        }),
        ('Charts', {
            'fields': [
                ('field_view', 'field_view_tag'),
                ('dso_finder_chart', 'dso_finder_chart_tag'),
                ('finder_chart', 'finder_chart_tag')
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

    def get_form(self, request, obj=None, **kwargs):
        form = super(DSOAdmin, self).get_form(request, obj, **kwargs)
        field = form.base_fields['constellation']
        field.widget.can_add_related = False
        field.widget.can_change_related = False
        field.widget.can_delete_related = False
        field = form.base_fields['object_type']
        field.widget.can_delete_related = False
        return form

admin.site.register(DSO, DSOAdmin)
