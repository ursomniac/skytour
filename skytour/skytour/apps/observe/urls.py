from django.urls import path
from .views import (
    ObservingLocationDetailView, 
    ObservingLocationUpdateView,
    ObservingLocationListView,
    ObservingLocationAddView,
    ObservingLocationDeleteView,
    ObservingLocationDeleteResultView
)

urlpatterns = (
    path('', ObservingLocationListView.as_view(), name='observing-location-list'),
    path('add', ObservingLocationAddView.as_view(), name='observing-location-add'),
    path('update/<int:pk>', ObservingLocationUpdateView.as_view(), name='observing-location-update'),
    path('delete/<int:pk>', ObservingLocationDeleteView.as_view(), name='observing-location-delete'),
    path('delete/result', ObservingLocationDeleteResultView.as_view(), name='observing-location-delete-result'),
    path('<int:pk>', ObservingLocationDetailView.as_view(), name='observing-location-detail'),
)