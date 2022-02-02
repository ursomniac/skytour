from django.contrib import admin

class AbstractObservation(admin.StackedInline):
    extra = 0
    fieldsets = (
    (None, {
        'fields': [
            ('ut_date', 'ut_time'),
            ('seeing', 'sqm'),
            ('telescope', 'eyepieces'),
            'notes',
        ]
    }),
)

    class Meta:
        abstract = True