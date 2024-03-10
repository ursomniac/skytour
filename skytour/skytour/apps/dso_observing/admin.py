from django.contrib import admin
from django.utils.html import mark_safe
from .models import TargetDSO, TargetObservingMode

class TargetObservingModeInline(admin.StackedInline):
    model = TargetObservingMode
    extra = 0
    fieldsets = (
        (None, {
            'fields': [
                ('mode','viable', 'priority'),
                ('interesting', 'challenging'),
                'issues',
                'description_flags',
                'notes'
            ]
        }),
    )

class TargetDSOAdmin(admin.ModelAdmin):
    model = TargetDSO
    inlines = [TargetObservingModeInline]
    readonly_fields = [
        'dso', 'mode_set', 'seed_entry',
        'get_coordinates', 'dso_page_button', 'dso_object_type',
        'dso_priorities', 'dso_magnitudes', 'dso_angular_size',
        'dso_names'
    ]
    list_display = [
        'pk', 
        'get_constellation', 
        'get_dso_name', 
        'dso_object_type',
        'ready_to_go', 
        'seed_entry',
        'mode_set',
        'dso_priorities'
    ]
    fieldsets = (
        (None, {
            'fields': [
                ('dso', 'seed_entry', 'status'),
                ('get_coordinates', 'dso_page_button', 'dso_object_type'),
                ('dso_priorities', 'dso_magnitudes', 'dso_angular_size'),
                ('ready_to_go', 'dso_names'),
                'notes'
            ]
        }),
    )
    search_fields = ['dso__shown_name']
    list_filter = ['dso__constellation__abbreviation']
    save_on_top = True

    def list_mode_set(self, obj):
        return obj.mode_set
    
    @admin.display(description='Con', ordering='dso__constellation__abbreviation')
    def get_constellation(self, obj):
        return obj.dso.constellation.abbreviation
    
    @admin.display(description='DSO Name', ordering='dso__shown_name')
    def get_dso_name(self, obj):
        return obj.dso.shown_name
    
    @admin.display(description="Coordinates")
    def get_coordinates(self, obj):
        return f"{obj.dso.ra_text}, {obj.dso.dec_text}"
    
    @admin.display(description='DSO Button')
    def dso_page_button(self, obj):
        href = f"/dso/{obj.dso.pk}"
        return mark_safe(f"""<a href="{href}" target="_new">DSO Page for {obj.dso.shown_name}</a>""")
    
    @admin.display(description='Priorities')
    def dso_priorities(self, obj):
        return f"{obj.dso.priority} / {obj.dso.imaging_checklist_priority}"
    
    @admin.display(description='Observing')
    def dso_magnitudes(self, obj):
        return f"Mag: {obj.dso.magnitude} SB: {obj.dso.surface_brightness} CI: {obj.dso.contrast_index}"

    @admin.display(description='Angular Size')
    def dso_angular_size(self, obj):
        x = f"Size: {obj.dso.angular_size}"
        if obj.dso.orientation_angle:
            x += f" at {obj.dso.orientation_angle}°"
        return x
    
    @admin.display(description='Object Type', ordering='dso__object_type__code')
    def dso_object_type(self, obj):
        x = f"{obj.dso.object_type.code}"
        if obj.dso.morphological_type:
            x += f" {obj.dso.morphological_type}"
        return x
    
    @admin.display(description='DSO Names')
    def dso_names(self, obj):
        x = ''
        if obj.dso.nickname is not None:
            x += obj.dso.nickname
        if obj.dso.alias_list is not None:
            x += f" = {obj.dso.alias_list}"
        return x

class TargetObservingModeAdmin(admin.ModelAdmin):
    model = TargetObservingMode
    readonly_fields = ['target_dso', 'target_constellation']
    list_display = ['pk', 'target_dso', 'target_constellation', 'mode', 'viable', 'priority']
    list_filter = ['mode', 'viable', 'priority']
    search_fields = ['target__dso__shown_name']

    @admin.display(description='DSO', ordering='target__dso__shown_name')
    def target_dso(self, obj):
        return obj.target.dso
    
    @admin.display(description='Constellation', ordering='target__dso__constellation__abbreviation')
    def target_constellation(self, obj):
        return obj.target.dso.constellation.abbreviation
    
admin.site.register(TargetDSO, TargetDSOAdmin)
admin.site.register(TargetObservingMode, TargetObservingModeAdmin)