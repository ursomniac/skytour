from django.urls import path
from .views import (
    AsteroidListView,
    AsteroidEditView,
    AsteroidDetailView,
    AsteroidObservationEditView,
    AsteroidRealTimeView,
    AsteroidManageListView,
)

urlpatterns = (
    path('', AsteroidListView.as_view(), name='asteroid-list'),
    path('edit/list', AsteroidManageListView.as_view(), name='asteroid-edit-list'),
    path('edit/<int:pk>', AsteroidEditView.as_view(), name='asteroid-edit'),
    path('observation/edit/<int:pk>', AsteroidObservationEditView.as_view(), name='asteroid-observe-edit'),
    path('real-time/<slug:slug>', AsteroidRealTimeView.as_view(), name='asteroid-real-time'),
    path('<slug:slug>', AsteroidDetailView.as_view(), name='asteroid-detail'),
)