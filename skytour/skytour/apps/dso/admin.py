from django.contrib import admin
from admin_auto_filters.filters import AutocompleteFilter
from ..abstract.admin import AbstractObservation, ObservableObjectAdmin, TagModelAdmin
from .models import DSO, DSOImage, DSOAlias, DSOObservation, DSOList, AtlasPlate, AtlasPlateVersion

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
        'atlas_plate_list',
    ]
    list_filter = ['priority', 'show_on_skymap', 'object_type', 'ra_h', ConstellationFilter]
    search_fields = ['nickname', 'shown_name', 'aliases__shown_name']
    fieldsets = (
        (None, {
            'fields': [
                ('catalog', 'id_in_catalog'),
                ('constellation', 'show_on_skymap'),
                ('nickname', 'atlas_plate_list'),
                ('object_type', 'morphological_type', 'priority'),
                'tags',
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

    def atlas_plate_list(self, obj):
        plates = obj.atlasplate_set.order_by('plate_id')
        pp = []
        for p in plates:
            pp.append(p.plate_id)
        return pp
    atlas_plate_list.short_description = 'Plates'
    
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

@admin.action(description='Show on Plan PDF')
def add_to_plan(modeladmin, request, queryset):
    queryset.udpate(show_on_plan=1)

@admin.action(description='Do not show on Plan PDF')
def remove_from_plan(modeladmin, request, queryset):
    queryset.update(show_on_plan=0)

class DSOListAdmin(TagModelAdmin):
    model = DSOList
    list_display = ['pk', 'name', 'description', 'tag_list', 'show_on_plan', 'dso_count']
    list_display_links = ['pk', 'name']
    autocomplete_fields = ['dso']
    readonly_fields = ['dso_count']
    actions = [add_to_plan, remove_from_plan]

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if db_field.name == 'dso':
            kwargs['queryset'] = DSO.objects.exclude(priority='None')
            #kwargs['queryset'] = DSO.objects.all()
        return super(DSOListAdmin, self).formfield_for_manytomany(db_field, request, **kwargs)

class AtlasPlateVersionInline(admin.StackedInline):
    model = AtlasPlateVersion
    readonly_fields = ['plate_tag','shapes', 'reversed']
    fieldsets = [
        (None, {
            'fields': (
                ('shapes', 'reversed', 'image'),
                'plate_tag'
            )
        }),
    ]
    extra = 0

class AtlasPlateAdmin(TagModelAdmin):
    model = AtlasPlate
    list_display = ['plate_id', 'center_ra', 'center_dec', 'center_constellation',  'con_list', 'tag_list', 'dso_count']
    autocomplete_fields = ['dso', 'constellation']
    readonly_fields = [
        'con_list', 
        'dso_count', 
        'center_constellation',
        'tag_list'
    ]
    fieldsets = [
        (None, {
            'fields': (
                'plate_id',
                ('center_ra', 'center_dec'),
                'tags',
                ('dso','constellation'),
            )
        }),
    ]
    save_on_top = True
    inlines = [AtlasPlateVersionInline,]

    def con_list(self, object):
        cc = []
        for c in object.constellation.all():
            cc.append(c.abbreviation)
        return ', '.join(cc)
    con_list.short_description = 'Constellations'

    def dso_count(self, object):
        return object.dso.count()
    dso_count.short_description = '# DSOs'

    def tag_list(self, object):
        tags = object.tags.values().order_by('name')
        tlist = []
        for t in tags:
            tlist.append(t['name'])
        return ', '.join(tlist)
    tag_list.short_description = 'Tags'

admin.site.register(DSO, DSOAdmin)
admin.site.register(DSOList, DSOListAdmin)
admin.site.register(AtlasPlate, AtlasPlateAdmin)