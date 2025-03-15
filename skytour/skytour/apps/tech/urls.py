from django.urls import path
from .views import (
    EyepieceListView,
    EyepieceUpdateView,
    EyepieceEditResultView,
    EyepieceDeleteView,
    EyepieceDeleteResultView,
    FilterListView,
    FilterUpdateView,
    FilterEditResultView,
    FilterDeleteView,
    FilterDeleteResultView,
    TelescopeListView,
    TelescopeUpdateView,
    TelescopeEditResultView,
    TelescopeDeleteView,
    TelescopeDeleteResultView,
)

urlpatterns = (
    path('telescope', TelescopeListView.as_view(), name='telescope-list'),
    path('telescope/edit/<int:pk>', TelescopeUpdateView.as_view(), name='telescope-edit'),
    path('telescope/edit/result', TelescopeEditResultView.as_view(), name='telescope-edit-result'),
    path('telescope/delete/<int:pk>', TelescopeDeleteView.as_view(), name='telescope-delete'),
    path('telescope/delete/result', TelescopeDeleteResultView.as_view(), name='telescope-delete-result'),

    path('eyepiece', EyepieceListView.as_view(), name='eyepiece-list'),
    path('eyepiece/edit/<int:pk>', EyepieceUpdateView.as_view(), name='eyepiece-edit'),
    path('eyepiece/edit/result', EyepieceEditResultView.as_view(), name='eyepiece-edit-result'),
    path('eyepiece/delete/<int:pk>', EyepieceDeleteView.as_view(), name='eyepiece-delete'),
    path('eyepiece/delete/result', EyepieceDeleteResultView.as_view(), name='eyepiece-delete-result'),

    path('filter', FilterListView.as_view(), name='filter-list'),
    path('filter/edit/<int:pk>', FilterUpdateView.as_view(), name='filter-edit'),
    path('filter/edit/result', FilterEditResultView.as_view(), name='filter-edit-result'),
    path('filter/delete/<int:pk>', FilterDeleteView.as_view(), name='filter-delete'),
    path('filter/delete/result', FilterDeleteResultView.as_view(), name='filter-delete-result')
)