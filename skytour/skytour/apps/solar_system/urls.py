from django.urls import path
from .views import (
    MoonDetailView,
    OrreryView,
    PlanetListView, 
    PlanetDetailView, 
)

urlpatterns = (
    path('', PlanetListView.as_view(), name='planet-list'),
    path('moon', MoonDetailView.as_view(), name='moon-detail'),
    path('orrery', OrreryView.as_view(), name='orrery'),
    path('<slug:slug>', PlanetDetailView.as_view(), name='planet-detail'),
)