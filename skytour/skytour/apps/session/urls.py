from django.urls import path
from .views import (
    ObservingPlanView,
    SetSessionCookieView,
    ObservingSessionListView, 
    ObservingSessionDetailView,
    SessionAddView,
    ShowCookiesView,
)

urlpatterns = (
    path('', ObservingSessionListView.as_view(), name='session-list'),
    path('<int:pk>', ObservingSessionDetailView.as_view(), name='session-detail'),
    path('cookie', SetSessionCookieView.as_view(), name='session-set'),
    path('plan', ObservingPlanView.as_view(), name='observing-plan'),
    path('show_cookies', ShowCookiesView.as_view(), name='show-cookies'),
    path('add', SessionAddView.as_view(), name='session-add'),
)