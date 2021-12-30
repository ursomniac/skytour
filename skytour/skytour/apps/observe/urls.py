from django.urls import path
from .views import (
    ObservingLocationDetailView, 
    ObservingLocationListView, 
)

urlpatterns = (
    path('', ObservingLocationListView.as_view(), name='observing-location-list'),
    path('<int:pk>', ObservingLocationDetailView.as_view(), name='observing-location-detail'),
)