from django.contrib import admin
from django.utils.html import mark_safe
from .models import (
    Calendar, CalendarEventReference,
    EventType,
    Glossary,
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

class GlossaryAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name", )}

class CalendarAdmin(admin.ModelAdmin):
    model = Calendar
    date_hierarchy = 'date'
    inlines = [CalendarEventReferenceInline]
    list_display = ['pk',  'date', 'time', 'title', 'event_type', 'reference_list']
    list_filter = ['date', 'event_type']
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
    #search_fields = ['title',]
    save_on_top = True

class WebsiteAdmin(admin.ModelAdmin):
    model = Website
    list_display = ['name', 'get_url_link']
    readonly_fields = ['get_url_link']

    def get_url_link(self, obj):
        return mark_safe(f'<a href="{obj.url}" target="_new">{obj.url}')
    get_url_link.short_description = 'Link'

class TimeZoneAdmin(admin.ModelAdmin):
    model = TimeZone
    list_display = ['pk', 'name', 'utc_offset']

admin.site.register(Calendar, CalendarAdmin)
admin.site.register(EventType, EventTypeAdmin)
admin.site.register(Glossary, GlossaryAdmin)
admin.site.register(StateRegion)
admin.site.register(TimeZone, TimeZoneAdmin)
admin.site.register(Website, WebsiteAdmin)