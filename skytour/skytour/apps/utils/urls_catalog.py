from django.urls import path
from .views import CatalogDetailView, CatalogListView

urlpatterns = (
    path('', CatalogListView.as_view(), name='catalog-list'),
    path('<int:pk>', CatalogDetailView.as_view(), name='catalog-detail'),
)
