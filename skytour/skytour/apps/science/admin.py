from django.contrib import admin
from .models import AsteroidOccultation, OccultingAsteroid, OccultedStar

class OccultingAsteroidAdmin(admin.ModelAdmin):
    model = OccultingAsteroid

class OccultedStarAdmin(admin.ModelAdmin):
    model = OccultedStar
    fieldsets = (
        (None, {
            'fields': [
                ('name', 'alias_list'),
                ('ra_h', 'ra_m', 'ra_s'),
                ('dec_sign', 'dec_d', 'dec_m', 'dec_s'),
                ('magnitude', 'color_index', 'parallax'),

            ]
        }),
    )
class AsteroidOccultationAdmin(admin.ModelAdmin):
    model = AsteroidOccultation
    readonly_fields = ['my_utdt', 'my_asteroid', 'my_star']
    list_display = [
        'pk', 'my_utdt', 'my_asteroid', 'my_star'
    ]
    fieldsets = (
        (None, {
            'fields': [
                ('observation_date', 'start_ut', 'duration'),
                ('asteroid', 'star'),
                'path_image',
                'notes'
            ]
        }),
    )

    def my_utdt(self, obj):
        return obj.formatted_utdt
    my_utdt.short_description = 'UT'

    def my_asteroid(self, obj):
        return obj.asteroid.shown_name
    my_asteroid.short_description = 'Asteroid'

    def my_star(self, obj):
        return obj.star.name
    my_star.short_description = 'Star'

admin.site.register(OccultedStar, OccultedStarAdmin)
admin.site.register(OccultingAsteroid, OccultingAsteroidAdmin)
admin.site.register(AsteroidOccultation, AsteroidOccultationAdmin)