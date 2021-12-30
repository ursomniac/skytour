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
from django.contrib import admin
from django.conf import settings
from django.urls import path, include
from django.conf.urls.static import static

urlpatterns = [
    path('', include('skytour.apps.site.urls')),
    path('admin/', admin.site.urls),
    path('catalog/', include('skytour.apps.utils.urls_catalog')),
    path('constellation/', include('skytour.apps.utils.urls_constellation')),
    path('dso/', include('skytour.apps.dso.urls_dso')),
    path('object_type/', include('skytour.apps.utils.urls_object_type')),
    path('observing_location/', include('skytour.apps.observe.urls')),
    path('plan/', include('skytour.apps.observe.urls_plan')),
    path('priority/', include('skytour.apps.dso.urls_priority')),
    path('stars/', include('skytour.apps.stars.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)\
    + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
