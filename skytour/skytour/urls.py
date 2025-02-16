"""skytour URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from ajax_select import urls as ajax_select_urls
from django.contrib import admin
from django.conf import settings
from django.urls import path, include
from django.conf.urls.static import static

admin.autodiscover()
urlpatterns = [
    path('', include('skytour.apps.site.urls')),
    path('ajax_select/', include(ajax_select_urls)),
    path('admin/', admin.site.urls),
    path('asteroid/', include('skytour.apps.solar_system.urls_asteroid')),
    path('astro/', include('skytour.apps.astro.urls')),
    path('atlas/', include('skytour.apps.dso.urls_atlas')),
    path('calendar/', include('skytour.apps.misc.urls_calendar')),
    path('catalog/', include('skytour.apps.utils.urls_catalog')),
    path('checklist', include('skytour.apps.dso.urls_checklist')),
    path('comet/', include('skytour.apps.solar_system.urls_comet')),
    path('constellation/', include('skytour.apps.utils.urls_constellation')),
    path('custom/', include('skytour.apps.custom.urls')),
    path('dso/', include('skytour.apps.dso.urls_dso')),
    path('library/', include('skytour.apps.utils.urls_library')),
    path('misc/', include('skytour.apps.misc.urls')),
    path('object_type/', include('skytour.apps.utils.urls_object_type')),
    path('observing_location/', include('skytour.apps.observe.urls')),
    path('planet/', include('skytour.apps.solar_system.urls')),
    path('priority/', include('skytour.apps.dso.urls_priority')),
    path('session/', include('skytour.apps.session.urls')),
    path('site/', include('skytour.apps.site_parameter.urls')),
    path('solar_system/', include('skytour.apps.solar_system.urls_features')),
    path('sso_pdf/', include('skytour.apps.solar_system.urls_pdf')),
    path('stars/', include('skytour.apps.stars.urls')),
    path('targets/', include('skytour.apps.dso_observing.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)\
    + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
