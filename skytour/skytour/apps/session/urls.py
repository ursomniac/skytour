from django.urls import path
from .views import (
    SetSessionCookieView,
    ObservingCircumstancesView,
    ObservingCircumstancesEditView,
    ObservingConditionsFormView,
    ObservingSessionListView, 
    ObservingSessionCreateView,
    ObservingSessionDetailView,
    SessionAddView,
    ShowCookiesView,
    ObservingPlanV2View
)

urlpatterns = (
    path('', ObservingSessionListView.as_view(), name='session-list'),
    path('<int:pk>', ObservingSessionDetailView.as_view(), name='session-detail'),
    path('cookie', SetSessionCookieView.as_view(), name='session-set'),
    path('planv2', ObservingPlanV2View.as_view(), name='observing-plan-v2'),
    path('show_cookies', ShowCookiesView.as_view(), name='show-cookies'),
    path('create', ObservingSessionCreateView.as_view(), name='session-create'),
    path('add_object', SessionAddView.as_view(), name='session-add'),
    path('add_conditions', ObservingConditionsFormView.as_view(), name='session-conditions'),
    path('circumstances', ObservingCircumstancesView.as_view(), name='observing-circumstances'),
    path('circumstances/edit/<int:pk>', ObservingCircumstancesEditView.as_view(), name='condition-edit'),
)