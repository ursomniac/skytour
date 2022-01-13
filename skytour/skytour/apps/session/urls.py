from django.urls import path
from .views import (
    ObservingSessionView,
)

urlpatterns = (
    path('', ObservingSessionView.as_view(), name='observing-session'),
)