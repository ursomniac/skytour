from django.urls import path
from .views import HelpPopupView

urlpatterns = (
    path('<str:slug>', HelpPopupView.as_view(), name='popup-help-page'),
)