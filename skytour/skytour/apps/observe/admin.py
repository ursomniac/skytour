from django.contrib import admin
from .models import ObservingLocation, LocationImage

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

class ObservingLocationAdmin(admin.ModelAdmin):
    model = ObservingLocation
    inlines = [LocationImageInline]
    
    list_display = ['pk',  'status', 'travel_distance', 'city', 'get_state', 'street_address', 'latitude', 'longitude', 'bortle', 'sqm', 'brightness']
    readonly_fields = ['map_tag', 'earth_tag', 'bortle_tag']
    search_fields = ['name', 'city']
    list_filter = ['status', 'state']
    fieldsets = (
        (None, {
            'fields': [
                ('status', 'primary_user'), 
                ('name'),
                ('street_address',), 
                ('city', 'state', 'time_zone'),
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
                'horizon_blockage'
            ]
        })
    )

    def get_state(self, obj):
        return obj.state.slug
    get_state.admin_order_field = 'state'
    get_state.short_description = 'State'

admin.site.register(ObservingLocation, ObservingLocationAdmin)

