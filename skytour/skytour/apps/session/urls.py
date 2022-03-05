from django.urls import path
from .pdf import PlanPDFView
from .views import (
    ObservingPlanView,
    SetSessionCookieView,
    ObservingSessionListView, 
    ObservingSessionDetailView,
    ShowCookiesView,
)

urlpatterns = (
    path('', ObservingSessionListView.as_view(), name='session-list'),
    path('<int:pk>', ObservingSessionDetailView.as_view(), name='session-detail'),
    path('cookie', SetSessionCookieView.as_view(), name='session-set'),
    path('plan', ObservingPlanView.as_view(), name='observing-plan'),
    path('plan_pdf', PlanPDFView.as_view(), name='plan-pdf'),
    path('show_cookies', ShowCookiesView.as_view(), name='show-cookies')
)