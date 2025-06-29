from django.urls import path
from .views import (
    MoonDetailView,
    PlanetListView, 
    PlanetDetailView, 
    PlanetObservationEditView,
    MoonRealTimeView,
    PlanetRealTimeView,
    PlanetWikiPopup
)

urlpatterns = (
    path('', PlanetListView.as_view(), name='planet-list'),
    path('moon', MoonDetailView.as_view(), name='moon-detail'),
    path('observation/edit/<int:pk>', PlanetObservationEditView.as_view(), name='planet-observe-edit'),
    path('real-time/moon', MoonRealTimeView.as_view(), name='moon-real-time'),
    path('real-time/<slug:slug>', PlanetRealTimeView.as_view(), name='planet-real-time'),
    path('wiki/<int:pk>', PlanetWikiPopup.as_view(), name='planet-wiki-popup'),
    path('<slug:slug>', PlanetDetailView.as_view(), name='planet-detail'),
)