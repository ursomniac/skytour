from django.contrib import admin
from django.utils.html import mark_safe
from admin_auto_filters.filters import AutocompleteFilter
from ..abstract.admin import AbstractObservation, ObservableObjectAdmin, TagModelAdmin
from .models import DSO, DSOImage, DSOAlias, DSOObservation, \
    DSOList, AtlasPlate, AtlasPlateVersion, AtlasPlateConstellationAnnotation, \
    DSOLibraryImage, \
    AtlasPlateSpecial, AtlasPlateSpecialVersion, \
    DSOInField, DSOInFieldAlias, DSOObservingMode

class ConstellationFilter(AutocompleteFilter):
    title = 'Constellation'
    field_name = 'constellation'

class DSOObservingModeInline(admin.StackedInline):
    model = DSOObservingMode
    extra = 0
    fieldsets = (
        (None, {
            'fields': [
                ('mode','viable', 'priority'),
                ('interesting', 'challenging'),
                'notes'
            ]
        }),
    )

class DSOImageAdmin(admin.StackedInline):
    model = DSOImage
    extra = 0
    readonly_fields = ['object_image_tag']
    fieldsets =  (
        (None, {
            'fields': [
                'order_in_list',
                ('image', 'object_image_tag'),
                'notes'
            ]
        }),
    )

class DSOLibraryImageAdmin(admin.StackedInline):
    model = DSOLibraryImage
    extra = 0
    readonly_fields = ['object_image_tag']
    fieldsets =  (
        (None, {
            'fields': [
                ('order_in_list', 'ut_datetime'),
                ('telescope', 'exposure', 'image_processing_status'),
                ('image_orientation', 'image_cropping'), 
                ('use_in_carousel', 'use_as_map'),
                ('image', 'object_image_tag',),
                'notes'
            ]
        }),
    )

class DSOAliasInline(admin.TabularInline):
    model = DSOAlias
    extra = 1
    fields = ['catalog', 'id_in_catalog', 'alias_in_field', 'in_field_dso']

class DSOInFieldAliasInline(admin.TabularInline):
    model = DSOInFieldAlias
    extra = 0
    fields = ['catalog', 'id_in_catalog', 'alias_in_field', 'in_field_dso']


class DSOObservationAdmin(AbstractObservation):
    model = DSOObservation

class DSOInFieldInline(admin.StackedInline):
    model = DSOInField
    extra = 0
    fieldsets = (
        (None, {
            'fields': [
                ('catalog', 'id_in_catalog', 'constellation'),
                ('object_type', 'morphological_type', 'nickname'),
                ('ra_h', 'ra_m', 'ra_s'),
                ('dec_sign', 'dec_d', 'dec_m', 'dec_s'),
                'magnitude', 
                 ('angular_size', 'major_axis_size', 'minor_axis_size'), 
                ('surface_brightness', 'contrast_index', 'orientation_angle'),
                ('distance', 'distance_units'),
                ('other_parameters', 'notes'),
                'override_metadata',
            ]
        }),
    )

    def get_form(self, request, obj=None, **kwargs):
        form = super(DSOInFieldInline, self).get_form(request, obj, **kwargs)
        for field in ['constellation', 'object_type', 'catalog']:
            form.base_fields[field].widget.can_add_related = False
            form.base_fields[field].widget.can_change_related = False
            form.base_fields[field].widget.can_delete_related = False
        return form

    def get_formset(self, request, obj=None, **kwargs):
        """
        This just removes some of the widgets in the admin because you'll never
        add a new constellation, etc.
        """
        formset = super().get_formset(request, obj, **kwargs)
        for field_name in ['constellation', 'object_type', 'catalog']:
            field = formset.form.base_fields[field_name]
            field.widget.can_add_related = False
            field.widget.can_change_related = False
            field.widget.can_delete_related = False
        return formset

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
        'num_dsos_in_field',
        'img_pri',
        'reimage',
        'n_obs',
        'obs_date'
    ]
    list_display_links = ['pk', 'shown_name',]
    readonly_fields = [
        'field_view_tag', 
        'finder_chart_tag',
        'dso_finder_chart_tag',
        'dso_finder_chart_wide_tag',
        'dso_finder_chart_narrow_tag',
        'dso_imaging_chart_tag',
        'atlas_plate_list',
        'has_dso_imaging_chart',
        'dsoinfield_table',
        'img_pri',
        'num_dsos_in_field',
        'metadata'
    ]
    list_filter = [ConstellationFilter, 'priority', 'show_on_skymap', 'object_type', 'ra_h', 'catalog' ]
    search_fields = ['nickname', 'shown_name', 'aliases__shown_name']
    fieldsets = (
        (None, {
            'fields': [
                ('catalog', 'id_in_catalog'),
                ('constellation', 'show_on_skymap'),
                ('nickname', 'atlas_plate_list'),
                ('object_type', 'morphological_type'),
                ('reimage', 'tags', 'map_label'),
            ]
        }),
        ('Coordinates', {
            'fields': [
                ('ra_h', 'ra_m', 'ra_s'),
                ('dec_sign', 'dec_d', 'dec_m', 'dec_s'),
            ]
        }),
        ('Attributes', {
            'fields': [
                'magnitude', 
                ('angular_size', 'major_axis_size', 'minor_axis_size'), 
                ('surface_brightness', 'contrast_index', 'orientation_angle'),
                ('distance', 'distance_units'),
                ('other_parameters', 'notes'),
                'override_metadata',
            ]
        }),
        ('DSOs in Field', {
            'fields': [
                'dsoinfield_table',
            ]
        }),
        ('Charts', {
            'classes': ['collapse'],
            'fields': [
                ('dso_imaging_chart', 'dso_imaging_chart_tag'),
                ('field_view', 'field_view_tag'),
                ('dso_finder_chart', 'dso_finder_chart_tag'),
                ('finder_chart', 'finder_chart_tag'),
                ('dso_finder_chart_wide', 'dso_finder_chart_wide_tag'),
                ('dso_finder_chart_narrow', 'dso_finder_chart_narrow_tag'),
                'pdf_page'
            ]
        }),
        ('Metadata', {
            'classes': ['collapse'],
            'fields': [
                ('hyperleda_name', 'simbad_name'),
                'metadata',
                'simbad'
            ]
        })
    )
    inlines = [
        DSOAliasInline, 
        DSOInFieldInline,
        DSOLibraryImageAdmin, 
        DSOImageAdmin,  
        DSOObservationAdmin,
        DSOObservingModeInline,
    ]
    actions = ['turn_on_redo', 'turn_off_redo']

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
    maj_axis.short_description = 'Size'

    def img_pri(self, obj):
        return obj.mode_imaging_priority
    img_pri.short_description = 'IP'

    def atlas_plate_list(self, obj):
        plates = obj.atlasplate_set.order_by('plate_id')
        pp = []
        for p in plates:
            pp.append(p.plate_id)
        return pp
    atlas_plate_list.short_description = 'Plates'

    def has_dso_imaging_chart(self, obj):
        return bool(obj.dso_imaging_chart) # Yeah, this is weird...
    has_dso_imaging_chart.short_description = 'Chart'
    has_dso_imaging_chart.boolean = True

    def num_dsos_in_field(self, obj):
        return obj.dsos_in_field_count
    num_dsos_in_field.short_description = 'Field'
    
    def get_form(self, request, obj=None, **kwargs):
        form = super(DSOAdmin, self).get_form(request, obj, **kwargs)
        for field in ['constellation', 'object_type', 'catalog']:
            form.base_fields[field].widget.can_add_related = False
            form.base_fields[field].widget.can_change_related = False
            form.base_fields[field].widget.can_delete_related = False
        return form
    
    @admin.action(description="Add to REDO image")
    def turn_on_redo(modeladmin, request, queryset):
        queryset.update(reimage=True)

    @admin.action(description="Remove from REDO List")
    def turn_off_redo(modeladmin, request, queryset):
        queryset.update(reimage=False)

class DSOListAdmin(TagModelAdmin):
    model = DSOList
    list_display = ['pk', 'name', 'description', 'tag_list', 'active_observing_list', 'dso_count']
    list_display_links = ['pk', 'name']
    autocomplete_fields = ['dso']
    readonly_fields = ['dso_count']
    actions = ['make_list_active', 'make_list_inactive']
    save_on_top = True

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if db_field.name == 'dso':
            kwargs['queryset'] = DSO.objects.exclude(priority='None')
            #kwargs['queryset'] = DSO.objects.all()
        return super(DSOListAdmin, self).formfield_for_manytomany(db_field, request, **kwargs)

    @admin.action(description='Make List Active')
    def make_list_active(modeladmin, request, queryset):
        queryset.update(active_observing_list=True)

    @admin.action(description="Make list inactive")
    def make_list_inactive(modeladmin, request, queryset):
        queryset.update(active_observing_list=False)

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

class AtlasPlateSpecialVersionInline(admin.StackedInline):
    model = AtlasPlateSpecialVersion
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

class AtlasPlateConstellationAnnotationInline(admin.TabularInline):
    model = AtlasPlateConstellationAnnotation
    extra = 0

class AtlasPlateAdmin(TagModelAdmin):
    model = AtlasPlate
    list_display = [
        'plate_id', 
        'format_ra', 
        'format_dec', 
        'center_constellation',  
        'con_list', 
        'tag_list', 
        'dso_count'
    ]
    autocomplete_fields = ['dso', 'constellation']
    readonly_fields = [
        'con_list', 
        'dso_count', 
        'format_ra',
        'format_dec',
        'center_constellation',
        'tag_list'
    ]
    fieldsets = [
        (None, {
            'fields': (
                'plate_id',
                ('center_ra', 'center_dec', 'radius'),
                'tags',
                ('dso','constellation'),
            )
        }),
    ]
    save_on_top = True
    inlines = [AtlasPlateVersionInline, AtlasPlateConstellationAnnotationInline]

    def format_ra(self, obj):
        return f"{obj.center_ra:.2f}"
    format_ra.short_description = 'R.A.'
    format_ra.admin_order_field = 'center_ra'

    def format_dec(self, obj):
        return f"{obj.center_dec:.1f}"
    format_dec.short_description = "Dec."
    format_dec.admin_order_field = 'center_dec'

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

class AtlasPlateSpecialAdmin(TagModelAdmin):
    model = AtlasPlate
    list_display = [
        'plate_id', 
        'title',
        'format_ra', 
        'format_dec', 
        'center_constellation',  
        'con_list', 
        'tag_list', 
        'dso_count'
    ]
    autocomplete_fields = ['dso', 'constellation']
    readonly_fields = [
        'con_list', 
        'dso_count', 
        'format_ra',
        'format_dec',
        'center_constellation',
        'tag_list'
    ]
    fieldsets = [
        (None, {
            'fields': (
                'plate_id',
                'title',
                ('center_ra', 'center_dec', 'radius'),
                'tags',
                ('dso','constellation'),
            )
        }),
    ]
    save_on_top = True
    inlines = [AtlasPlateSpecialVersionInline,]

    def format_ra(self, obj):
        return f"{obj.center_ra:.2f}"
    format_ra.short_description = 'R.A.'
    format_ra.admin_order_field = 'center_ra'

    def format_dec(self, obj):
        return f"{obj.center_dec:.1f}"
    format_dec.short_description = "Dec."
    format_dec.admin_order_field = 'center_dec'

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

class DSOInFieldAdmin(admin.ModelAdmin):
    model = DSOInField
    autocomplete_fields = ['parent_dso']
    search_fields = ['nickname', 'shown_name', 'parent_dso__shown_name']
    list_display = ['pk', 'shown_name', 'parent_dso', 'object_type', 'morphological_type', 'magnitude', 'angular_size', 'distance_to_primary']
    readonly_fields = ['distance_to_primary']
    save_on_top = True
    fieldsets = (
        (None, {
            'fields': [
                ('catalog', 'id_in_catalog', 'constellation'),
                ('object_type', 'morphological_type', 'nickname'),
                'parent_dso'
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
                ('surface_brightness', 'contrast_index', 'orientation_angle'),
                ('distance', 'distance_units'),
                ('other_parameters','notes'),
                'override_metadata',
            ]
        }),
        ('Metadata', {
            'classes': ['collapse'],
            'fields': [
                ('hyperleda_name', 'simbad_name'),
                'metadata',
                'simbad'
            ]
        })
    )
    inlines = [DSOInFieldAliasInline]

    @admin.display(description='From Primary')
    def distance_to_primary(self, obj):
        return f"{obj.primary_distance:5.1f}\' at {obj.primary_angle:5.1f}°"

admin.site.register(DSO, DSOAdmin)
admin.site.register(DSOList, DSOListAdmin)
admin.site.register(DSOInField, DSOInFieldAdmin)
admin.site.register(AtlasPlate, AtlasPlateAdmin)
admin.site.register(AtlasPlateSpecial, AtlasPlateSpecialAdmin)
