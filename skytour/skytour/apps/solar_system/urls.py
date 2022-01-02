from django.urls import path
from .views import (
    PlanetListView, 
    PlanetDetailView, 
)

urlpatterns = (
    path('', PlanetListView.as_view(), name='planet-list'),
    path('<slug:slug>', PlanetDetailView.as_view(), name='planet-detail'),
)