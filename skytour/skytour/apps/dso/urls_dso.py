from django.urls import path
from .views import (
    AvailableDSOObjectsView,    
    DSODetailView, 
    DSOListView, 
    DSOAdjustDSOListView,
    DSOFilterView, 
    DSOCreateList,
    DSOListActiveView,
    DSOListDetailView,
    DSOListListView,
    DSOObservationLogView,
    DSORealTimeView,
    DSOSearchView,
    DSOEditMetadataView,
    DSOManageImageView
)
urlpatterns = (
    path('', DSOListView.as_view(), name='dso-list'),
    path('available', AvailableDSOObjectsView.as_view(), name='dso-available-objects'),
    path('create_dso_list', DSOCreateList.as_view(), name='dso-create-list'),
    path('filter', DSOFilterView.as_view(), name='dso-filter'),
    path('list/<int:pk>', DSOListDetailView.as_view(), name='dsolist-detail'),
    path('list/adjustlist/<str:op>/<int:pk>', DSOAdjustDSOListView.as_view(), name='dsolist-adjust'),
    path('list/dsoactive', DSOListActiveView.as_view(), name='dsolist-active'),
    path('list', DSOListListView.as_view(), name='dsolist-list'),
    path('observe', DSOObservationLogView.as_view(), name='dso-observed'),
    path('real-time/<int:pk>', DSORealTimeView.as_view(), name='dso-real-time'),
    path('search', DSOSearchView.as_view(), name='dso-name-search'),
    path('edit/<int:pk>', DSOEditMetadataView.as_view(), name='dso-edit-metadata'),
    path('image/edit/<int:pk>',DSOManageImageView.as_view(), name='dso-manage-image'),
    path('<int:pk>', DSODetailView.as_view(), name='dso-detail'),
)