from django.contrib import admin
from .models import ObservingSession, ObservingCircumstances

class ObservingCircumstancesInline(admin.StackedInline):
    model = ObservingCircumstances
    extra = 0
    fieldsets = [
        (None, {
            'fields': [
                ('session_stage', 'ut_datetime'),
                ('temperature', 'humidity', 'cloud_cover'),
                ('seeing', 'sqm')
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

admin.site.register(ObservingSession, ObservingSessionAdmin)