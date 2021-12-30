from django.urls import path
from .views import (
    ObservingPlanView,
)

urlpatterns = (
    path('', ObservingPlanView.as_view(), name='observing-plan'),
)