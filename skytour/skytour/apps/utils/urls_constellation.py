from django.urls import path
from .views import ConstellationDetailView, ConstellationListView

urlpatterns = (
    path('', ConstellationListView.as_view(), name='constellation-list'),
    path('<slug:slug>', ConstellationDetailView.as_view(), name='constellation-detail'),
)