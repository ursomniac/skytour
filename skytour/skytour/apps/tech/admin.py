from django.contrib import admin
from .models import Telescope, Eyepiece, Filter

class EyepieceAdmin(admin.ModelAdmin):
    model = Eyepiece
    readonly_fields = ['mag_display', 'fov_display']
    list_display = ['pk', 'focal_length', 'telescope', 'mag_display', 'fov_display']

admin.site.register(Telescope)
admin.site.register(Eyepiece, EyepieceAdmin)
admin.site.register(Filter)