from django.urls import path
from .views import (
    ObservingPlanView,
    SetSessionCookieView
)

urlpatterns = (
    path('', SetSessionCookieView.as_view(), name='session-set'),
    path('plan', ObservingPlanView.as_view(), name='observing-plan')
)