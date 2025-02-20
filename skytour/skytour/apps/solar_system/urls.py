from django.urls import path
from .views import (
    MoonDetailView,
    PlanetListView, 
    PlanetDetailView, 
    PlanetRealTimeView
)

urlpatterns = (
    path('', PlanetListView.as_view(), name='planet-list'),
    path('moon', MoonDetailView.as_view(), name='moon-detail'),
    path('real-time/<slug:slug>', PlanetRealTimeView.as_view(), name='planet-real-time'),
    path('<slug:slug>', PlanetDetailView.as_view(), name='planet-detail'),
)