from django.contrib import admin
from .models import Telescope, Eyepiece, Filter, Sensor

#class EyepieceInline(admin.TabularInline):
#    model = Eyepiece
#    extra = 0

#class FilterInline(admin.TabularInline):
#    model = Filter
#    extra = 0

class SensorInline(admin.StackedInline):
    model = Sensor
    fieldsets = (
        (
            None, 
            {'fields': [
                ('name', 'camera_name'), 
                ('pixels_x', 'pixels_y', 'pixel_size'),
                'order_in_list'
            ]}
        ),
    )
    extra = 0

class EyepieceAdmin(admin.ModelAdmin):
    model = Eyepiece
    readonly_fields = ['magnification', 'fov_display']
    list_display = ['pk', 'focal_length', 'telescope', 'magnification', 'fov_display']

class TelescopeAdmin(admin.ModelAdmin):
    model = Telescope
    list_display = ['pk', 'name', 'aperture', 'focal_length', 'sensor_field_of_view', 'sensor_resolution', 'order_in_list']
    readonly_fields = ['sensor_field_of_view', 'sensor_resolution']
    inlines = [SensorInline]

    def sensor_field_of_view(self, object):
        sens = object.sensor_set.first()
        if sens is None:
            return None
        (fovx, fovy) = sens.field_of_view
        return f"{fovx:.1f}\' x {fovy:.1f}\'"
    
    def sensor_resolution(self, object):
        sens = object.sensor_set.first()
        if sens is None:
            return None
        res = sens.pixel_resolution
        return f"{res:.1f}" # arcsec

admin.site.register(Telescope, TelescopeAdmin)
admin.site.register(Eyepiece, EyepieceAdmin)
admin.site.register(Filter)