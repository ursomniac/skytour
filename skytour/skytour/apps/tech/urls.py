from django.urls import path
from .views import (
    TelescopeListView,
    TelescopeUpdateView,
    TelescopeEditResultView,
    TelescopeDeleteView,
    TelescopeDeleteResultView
)

urlpatterns = (
    path('telescope', TelescopeListView.as_view(), name='telescope-list'),
    path('telescope/edit/<int:pk>', TelescopeUpdateView.as_view(), name='telescope-edit'),
    path('telescope/edit/result', TelescopeEditResultView.as_view(), name='telescope-edit-result'),
    path('telescope/delete/<int:pk>', TelescopeDeleteView.as_view(), name='telescope-delete'),
    path('telescope/delete/result', TelescopeDeleteResultView.as_view(), name='telescope-delete-result')
)