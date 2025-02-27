from django.urls import path
from .views import HelpPageView, HelpPopupView

urlpatterns = (
    path('', HelpPageView.as_view(), name='main-help-page'),
    path('popup/<str:slug>', HelpPopupView.as_view(), name='popup-help-page'),
    path('<str:slug>', HelpPageView.as_view(), name='help-page')
)