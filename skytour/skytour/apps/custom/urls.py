from django.urls import path
from .views import (
    HomeObjectsView, CookieObjectsView
)
urlpatterns = (
    path('', HomeObjectsView.as_view(), name='home-objects'),
    path('cookie', CookieObjectsView.as_view(), name = 'cookie-objects')
)