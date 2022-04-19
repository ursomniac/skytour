from django.urls import path
from .views import AtlasPlateListView, AtlasPlateDetailView

urlpatterns = (
    path('', AtlasPlateListView.as_view(), name='atlas-list'),
    path('<slug:slug>', AtlasPlateDetailView.as_view(), name='atlas-detail'),
)