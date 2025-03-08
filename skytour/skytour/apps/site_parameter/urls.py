from django.urls import path
from .views import (
    SiteParameterListView,
    SiteParameterEditView,
    SiteParameterEditResultView,
)

urlpatterns = (
    path('', SiteParameterListView.as_view(), name='site-parameter-list' ),
    path('edit/<str:ptype>/<int:pk>', SiteParameterEditView.as_view(), name='site-parameter-edit'),
    path('edit/result', SiteParameterEditResultView.as_view(), name='param-edit-result'),
)