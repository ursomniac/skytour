from django.urls import path
from .views import (
    HomeObjectsView
)
urlpatterns = (
    path('', HomeObjectsView.as_view(), name='home-objects'),
)