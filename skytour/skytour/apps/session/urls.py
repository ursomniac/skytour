from django.urls import path
from .pdf import PlanPDFView, CustomPlanPDFFormView, CustomPlanPDFView
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
    path('custom_plan', CustomPlanPDFFormView.as_view(), name='custom-plan'),
    path('custom_plan_pdf', CustomPlanPDFView.as_view(), name='custom-plan-pdf'),
    path('show_cookies', ShowCookiesView.as_view(), name='show-cookies')
)