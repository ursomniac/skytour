from django.urls import path
from .views import SiteParameterLinkList

urlpatterns = (
    path('links', SiteParameterLinkList.as_view(), name='link-list'),
)