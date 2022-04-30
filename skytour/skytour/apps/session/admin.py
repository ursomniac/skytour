from django.contrib import admin
from .models import ObservingSession, ObservingCircumstances

class ObservingCircumstancesInline(admin.StackedInline):
    model = ObservingCircumstances
    extra = 0
    fieldsets = [
        (None, {
            'fields': [
                ('session_stage', 'ut_datetime'),
                ('temperature', 'humidity'), 
                ('cloud_cover', 'wind'),
                ('seeing', 'sqm'),
                'notes'
            ]
        }),
    ]

class ObservingSessionAdmin(admin.ModelAdmin):
    model = ObservingSession
    list_display = ['ut_date', 'location']
    fieldsets = (
        (None, {
            'fields': [
                'ut_date',
                'location',
                'notes'
            ]
        }),
    )
    inlines = [ObservingCircumstancesInline]

class ObservingCircumstancesAdmin(admin.ModelAdmin):
    model = ObservingCircumstances
    list_display = [
        'pk', 'session', 'session_stage', 'sqm', 'seeing_number', 'temperature', 'wind'
    ]
    readonly_fields = ['seeing_number']

    def seeing_number(self, object):
        return object.seeing
    seeing_number.short_description = 'Seeing'


admin.site.register(ObservingSession, ObservingSessionAdmin)
admin.site.register(ObservingCircumstances, ObservingCircumstancesAdmin)