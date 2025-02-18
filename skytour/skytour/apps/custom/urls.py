from django.urls import path
from .views import DSOObjectsView

urlpatterns = (
    path('', DSOObjectsView.as_view(), name='dso-objects'),
)