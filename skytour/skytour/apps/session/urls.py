from django.urls import path
from .views import (
    ObservingPlanView,
    SetSessionCookieView,
    ObservingCircumstancesView,
    ObservingConditionsFormView,
    ObservingSessionListView, 
    ObservingSessionCreateView,
    ObservingSessionDetailView,
    SessionAddView,
    ShowCookiesView,
    ObservingLogView
)

urlpatterns = (
    path('', ObservingSessionListView.as_view(), name='session-list'),
    path('<int:pk>', ObservingSessionDetailView.as_view(), name='session-detail'),
    path('cookie', SetSessionCookieView.as_view(), name='session-set'),
    path('plan', ObservingPlanView.as_view(), name='observing-plan'),
    path('show_cookies', ShowCookiesView.as_view(), name='show-cookies'),
    path('create', ObservingSessionCreateView.as_view(), name='session-create'),
    path('add_object', SessionAddView.as_view(), name='session-add'),
    path('add_conditions', ObservingConditionsFormView.as_view(), name='session-conditions'),
    path('observed', ObservingLogView.as_view(), name='observed-objects'),
    path('circumstances', ObservingCircumstancesView.as_view(), name='observing-circumstnaces')
)