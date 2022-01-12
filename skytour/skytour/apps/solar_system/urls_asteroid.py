from django.urls import path
from .views import (
    AsteroidListView,
    AsteroidDetailView
)

urlpatterns = (
    path('', AsteroidListView.as_view(), name='asteroid-list'),
    path('<slug:slug>', AsteroidDetailView.as_view(), name='asteroid-detail'),
)