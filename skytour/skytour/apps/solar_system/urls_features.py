from django.urls import path
from .views import (
    OrreryView,
    TrackerView,
    TrackerResultView
)

urlpatterns = (
    path('orrery', OrreryView.as_view(), name='orrery-view'),
    path('track', TrackerView.as_view(), name='object-track'),
    path('track_result', TrackerResultView.as_view(), name='track-result')
)