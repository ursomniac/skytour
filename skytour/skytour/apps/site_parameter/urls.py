from django.urls import path
from .views import SiteParameterListView

urlpatterns = (
    path('', SiteParameterListView.as_view(), name='site-parameter-list' ),
)