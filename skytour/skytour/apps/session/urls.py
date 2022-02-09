from django.urls import path
from .views import (
    ObservingPlanView,
    SetSessionCookieView,
    ObservingSessionListView, 
    ObservingSessionDetailView
)

urlpatterns = (
    path('', ObservingSessionListView.as_view(), name='session-list'),
    path('<int:pk>', ObservingSessionDetailView.as_view(), name='session-detail'),
    path('cookie', SetSessionCookieView.as_view(), name='session-set'),
    path('plan', ObservingPlanView.as_view(), name='observing-plan'),
)