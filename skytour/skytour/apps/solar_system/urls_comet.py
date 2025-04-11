from django.urls import path
from .views import (
    CometListView,
    CometDetailView,
    CometEditView,
    CometObservationEditView,
    CometRealTimeView,
    CometManageListView
)

urlpatterns = (
    path('', CometListView.as_view(), name='comet-list'),
    path('edit/list', CometManageListView.as_view(), name='comet-edit-list'),
    path('edit/<int:pk>', CometEditView.as_view(), name='comet-edit'),
    path('observation/edit/<int:pk>', CometObservationEditView.as_view(), name='comet-observe-edit'),
    path('real-time/<int:pk>', CometRealTimeView.as_view(), name='comet-real-time'),
    path('<int:pk>', CometDetailView.as_view(), name='comet-detail'),
)