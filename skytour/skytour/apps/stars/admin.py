from django.contrib import admin
from .models import BrightStar

class BrightStarAdmin(admin.ModelAdmin):
    model = BrightStar
    list_filter = ['constellation']

admin.site.register(BrightStar, BrightStarAdmin)
