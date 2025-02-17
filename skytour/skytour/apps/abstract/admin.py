from django.contrib import admin

class AbstractObservation(admin.StackedInline):
    """
    Used for:
        - DSO observations
        - Planet observations
        - Asteroid observations
        - Comet observations
    """
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

class ObservableObjectAdmin(admin.ModelAdmin):
    """
    Used for:
        - DSO Observations
        - Planet Observations
        - Comet Observations
        - Asteroid Observations
    """
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
    """
    Used for tagging.
    TODO V2: work out how to make this more useful
    """
    @admin.display(description='Tags')
    def tag_list(self, obj):
        return u", ".join(o.name for o in obj.tags.all())