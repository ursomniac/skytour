from django.urls import path
from .views import (
    MoonDetailView,
    PlanetListView, 
    PlanetDetailView, 
)

urlpatterns = (
    path('', PlanetListView.as_view(), name='planet-list'),
    path('moon', MoonDetailView.as_view(), name='moon-detail'),
    path('<slug:slug>', PlanetDetailView.as_view(), name='planet-detail'),
)