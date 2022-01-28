from django.urls import path
from .views import (
    AsteroidListView,
    AsteroidDetailView,
    AsteroidTrackView
)

urlpatterns = (
    path('', AsteroidListView.as_view(), name='asteroid-list'),
    path('<slug:slug>', AsteroidDetailView.as_view(), name='asteroid-detail'),
    path('track/<slug:slug>', AsteroidTrackView.as_view(), name='asteroid-track'),
)