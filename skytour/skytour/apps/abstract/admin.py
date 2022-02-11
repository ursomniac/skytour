from django.contrib import admin

class AbstractObservation(admin.StackedInline):
    extra = 0
    fieldsets = (
    (None, {
        'fields': [
            ('ut_datetime', 'location'),
            ('telescope', 'eyepieces', 'filters'),
            'notes',
        ]
    }),
)

    class Meta:
        abstract = True