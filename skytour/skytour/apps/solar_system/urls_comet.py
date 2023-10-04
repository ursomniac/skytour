from django.urls import path
from .views import (
    CometListView,
    CometDetailView,
    CometRealTimeView
)

urlpatterns = (
    path('', CometListView.as_view(), name='comet-list'),
    path('real-time/<int:pk>', CometRealTimeView.as_view(), name='comet-real-time'),
    path('<int:pk>', CometDetailView.as_view(), name='comet-detail'),
)