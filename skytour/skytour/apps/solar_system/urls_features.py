from django.urls import path
from .views import (
    OrreryView,
    SSOManageLibraryImagePanelView,
    SSOMapView,
    TrackerView,
    TrackerResultView
)

urlpatterns = (
    path('sso_map/<str:object_type>/<int:pk>/<str:style>', SSOMapView.as_view(), name='sso-map'),
    path('library/manage/<str:object_type>/<int:pk>', SSOManageLibraryImagePanelView.as_view(), name='sso-manage-library'),
    path('orrery', OrreryView.as_view(), name='orrery-view'),
    path('track', TrackerView.as_view(), name='object-track'),
    path('track_result', TrackerResultView.as_view(), name='track-result')
)