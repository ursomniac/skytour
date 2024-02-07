from django.urls import path
from .views import (
    TargetListView,
    TargetDetailView
)

urlpatterns = (
    path('', TargetListView.as_view(), name='target-list'),
    path('<int:pk>', TargetDetailView.as_view(), name='target-detail'),
)