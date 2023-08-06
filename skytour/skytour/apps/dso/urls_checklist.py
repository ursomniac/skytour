from django.urls import path
from .views import DSOChecklistView

urlpatterns = (
    path('', DSOChecklistView.as_view(), name='dso-checklist'),
)