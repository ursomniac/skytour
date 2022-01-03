from django.contrib import admin
from .models import (
    Calendar,
    EventType,
    StateRegion,
    TimeZone,
)

admin.site.register(Calendar)
admin.site.register(EventType)
admin.site.register(StateRegion)
admin.site.register(TimeZone)