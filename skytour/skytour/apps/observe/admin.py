from django.contrib import admin
from .models import ObservingLocation, LocationImage, ObservingLocationMask

class LocationImageInline(admin.StackedInline):
    model = LocationImage
    extra = 1
    readonly_fields = ['image_tag']
    fieldsets = (
        (None, {
            'fields': [
                'image_tag',
                ('image', 'direction'), 
                'description',
            ]
        }),
    )

class ObservingLocationMaskInline(admin.TabularInline):
    model = ObservingLocationMask
    fields = ['azimuth_start', 'altitude_start', 'azimuth_end', 'altitude_end']
    extra = 1

class ObservingLocationAdmin(admin.ModelAdmin):
    model = ObservingLocation
    inlines = [LocationImageInline, ObservingLocationMaskInline]
    
    list_display = [
        'pk',  'status', 'travel_distance', 'city', 'get_state', 'street_address', 
        'latitude', 'longitude', 'bortle', 'sqm', 'brightness',
        'n_sessions', 'last_session'
    ]
    readonly_fields = ['map_tag', 'earth_tag', 'bortle_tag', 'n_sessions', 'last_session']
    search_fields = ['name', 'city']
    list_filter = ['status', 'state']
    save_on_top = True
    fieldsets = (
        (None, {
            'fields': [
                'status', 
                ('name'),
                ('street_address',), 
                ('city', 'state', 'region', 'time_zone'),
                ('travel_distance', 'travel_time')
            ]
        }),
        ('Geospatial', {
            'fields': [
                ('latitude', 'longitude', 'elevation')
            ]
        }),
        ('Sky Brightness', {
            'fields': [
                ('bortle', 'sqm'),
                ('brightness', 'artificial_brightness', 'ratio'),
            ]
        }),
        ('Maps', {
            'fields': [
                ('map_image', 'map_tag'),
                ('earth_image', 'earth_tag'),
                ('bortle_image', 'bortle_tag')
            ]
        }),
        ('Site Issues', {
            'fields': [
                ('parking', 'is_flat'),
                'description',
                'light_sources',
                'horizon_blockage',
                'pdf_form'
            ]
        })
    )

    def n_sessions(self, obj):
        return obj.number_of_sessions
    n_sessions.short_description = '# Sessions'

    def get_state(self, obj):
        if obj.state:
            return obj.state.abbreviation
        return obj.region
    get_state.admin_order_field = 'state'
    get_state.short_description = 'State/Reg'

admin.site.register(ObservingLocation, ObservingLocationAdmin)
admin.site.register(ObservingLocationMask)
