from django.contrib import admin
from .models import Telescope, Eyepiece, Filter

class EyepieceAdmin(admin.ModelAdmin):
    model = Eyepiece
    readonly_fields = ['magnification', 'fov_display']
    list_display = ['pk', 'focal_length', 'telescope', 'magnification', 'fov_display']

class TelescopeAdmin(admin.ModelAdmin):
    model = Telescope
    list_display = ['pk', 'name', 'aperture', 'focal_length', 'order_in_list']

admin.site.register(Telescope, TelescopeAdmin)
admin.site.register(Eyepiece, EyepieceAdmin)
admin.site.register(Filter)