from django.urls import path
from .views import DSODetailView

urlpatterns = (
    path('<int:pk>', DSODetailView.as_view(), name='dso-detail'),
)