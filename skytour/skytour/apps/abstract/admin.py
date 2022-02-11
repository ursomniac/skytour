from django.contrib import admin

class AbstractObservation(admin.StackedInline):
    extra = 0
    fieldsets = (
    (None, {
        'fields': [
            ('ut_datetime', 'location'),
            ('telescope', 'eyepieces'),
            'notes',
        ]
    }),
)

    class Meta:
        abstract = True