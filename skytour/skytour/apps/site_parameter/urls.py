from django.urls import path
from .views import (
    SiteParameterListView,
    SiteParameterEditView,
    SiteParameterEditResultView,
    #SiteParameterEditPositiveIntegerView
)

urlpatterns = (
    path('', SiteParameterListView.as_view(), name='site-parameter-list' ),
    path('param/edit/<str:ptype>/<int:pk>', SiteParameterEditView.as_view(), name='site-parameter-edit'),
   #path('param/edit/positive/<int:pk>', SiteParameterEditPositiveIntegerView.as_view(), name='param-edit-positive'),
    path('param/edit/result', SiteParameterEditResultView.as_view(), name='param-edit-result'),
)