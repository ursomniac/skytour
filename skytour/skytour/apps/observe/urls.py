from django.urls import path
from .views import (
    ObservingLocationDetailView, 
    ObservingLocationUpdateView,
    ObservingLocationListView,
    ObservingLocationAddView 
)

urlpatterns = (
    path('', ObservingLocationListView.as_view(), name='observing-location-list'),
    path('add', ObservingLocationAddView.as_view(), name='observing-location-add'),
    path('update/<int:pk>', ObservingLocationUpdateView.as_view(), name='observing-location-update'),
    path('<int:pk>', ObservingLocationDetailView.as_view(), name='observing-location-detail'),
)