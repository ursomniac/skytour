from django.urls import path
from .views import (
    AstroCalcView, 
)

urlpatterns = (
    path('', AstroCalcView.as_view(), name='astro-calc'),
)