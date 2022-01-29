from django.contrib import admin
from .models import (
    Calendar, CalendarEventReference,
    EventType,
    StateRegion,
    TimeZone,
    Website,
)

class CalendarEventReferenceInline(admin.TabularInline):
    model = CalendarEventReference
    extra = 1

class EventTypeAdmin(admin.ModelAdmin):
    model = EventType

    list_display = ['pk', 'name', 'icon']

class CalendarAdmin(admin.ModelAdmin):
    model = Calendar
    inlines = [CalendarEventReferenceInline]
    list_display = ['pk',  'date', 'time', 'title', 'event_type', 'reference_list']
    readonly_fields = ['reference_list']
    fieldsets = (
        (None, {
            'fields': [
                ('date', 'time'),
                'event_type',
                'title',
                'description', 
            ]
        }),
    )


admin.site.register(Calendar, CalendarAdmin)
admin.site.register(EventType, EventTypeAdmin)
admin.site.register(StateRegion)
admin.site.register(TimeZone)
admin.site.register(Website)