from django.contrib import admin
from .models import (
    SiteParameterFloat,
    SiteParameterImage,
    SiteParameterPositiveInteger,
    SiteParameterLink,
    SiteParameterNumber,
    SiteParameterString
)

class AbstractAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("title", )}
    list_display = ('pk', 'title', 'slug', 'value')
    list_display_links = ('pk', 'title')
    ordering = ('slug', )
    search_fields = ['title',]
    readonly_fields = ['date_created', 'date_modified', 'pk']
    fieldsets = (
        (
            None,
            {
                'fields': (
                    ('pk', 'date_created', 'date_modified'), 
                    ('title', 'slug'),
                    'value', 
                    'description'
                ),
            },
        ),
    )

    class Meta:
        abstract = True

class SPFloatAdmin(AbstractAdmin):
    pass

class SPImageAdmin(AbstractAdmin):
    pass

class SPPositiveIntegerAdmin(AbstractAdmin):
    pass

class SPNumberAdmin(AbstractAdmin):
    pass

class SPStringAdmin(AbstractAdmin):
    pass

class SPLinkAdmin(AbstractAdmin):
    list_display = ('pk', 'title', 'slug', 'value', 'new_window')
    fieldsets = (
        (None, {
            'fields': (
                ('pk', 'date_created', 'date_modified'), 
                ('title', 'slug'),
                'value',
                'new_window',
                'description'
            ),
        },),
    )

admin.site.register(SiteParameterLink, SPLinkAdmin)
admin.site.register(SiteParameterNumber, SPNumberAdmin)
admin.site.register(SiteParameterPositiveInteger, SPPositiveIntegerAdmin)
admin.site.register(SiteParameterString, SPStringAdmin)
admin.site.register(SiteParameterFloat, SPFloatAdmin)
admin.site.register(SiteParameterImage, SPImageAdmin)