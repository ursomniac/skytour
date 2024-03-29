from django.contrib import admin

class AbstractObservation(admin.StackedInline):
    extra = 0
    fieldsets = (
        (None, {
            'fields': [
                ('ut_datetime', 'location'),
                ('telescope', 'eyepieces', 'filters'),
                ('num_images', 'imaging_status'),
                'notes',
            ]
        }),
    )

    class Meta:
        abstract = True

class ObservableObjectAdmin(admin.ModelAdmin):
    
    @admin.display(description='# Obs.')
    def n_obs(self, obj):
        return obj.number_of_observations

    @admin.display(description='Date')
    def obs_date(self, obj):
        if obj.last_observed is not None:
            return obj.last_observed.strftime("%Y-%m-%d")
        return None
    
    class Meta:
        abstract = True

class TagModelAdmin(admin.ModelAdmin):
    @admin.display(description='Tags')
    def tag_list(self, obj):
        return u", ".join(o.name for o in obj.tags.all())