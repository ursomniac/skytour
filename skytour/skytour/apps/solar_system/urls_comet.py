from django.urls import path
from .views import (
    CometListView,
    CometDetailView
)

urlpatterns = (
    path('', CometListView.as_view(), name='comet-list'),
    path('<int:pk>', CometDetailView.as_view(), name='comet-detail'),
)