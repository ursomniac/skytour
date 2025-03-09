from django.urls import path
from .views import (
    CometListView,
    CometDetailView,
    CometEditView,
    CometRealTimeView
)

urlpatterns = (
    path('', CometListView.as_view(), name='comet-list'),
    path('edit/<int:pk>', CometEditView.as_view(), name='comet-edit'),
    path('real-time/<int:pk>', CometRealTimeView.as_view(), name='comet-real-time'),
    path('<int:pk>', CometDetailView.as_view(), name='comet-detail'),
)