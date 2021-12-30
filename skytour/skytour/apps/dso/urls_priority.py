from django.urls import path
from .views import PriorityListView, PriorityDetailView

urlpatterns = (
    path('', PriorityListView.as_view(), name='priority-list'),
    path('<str:priority>', PriorityDetailView.as_view(), name='priority-detail'),
)