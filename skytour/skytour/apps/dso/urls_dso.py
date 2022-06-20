from django.urls import path
from .views import (
    DSODetailView, 
    DSOListView, 
    DSOFilterView, 
    DSOCreateList,
    DSOListListView,
    DSOListDetailView,
    DSOObservationLogView,
)
urlpatterns = (
    path('', DSOListView.as_view(), name='dso-list'),
    path('create_dso_list', DSOCreateList.as_view(), name='dso-create-list'),
    path('filter', DSOFilterView.as_view(), name='dso-filter'),
    path('list/<int:pk>', DSOListDetailView.as_view(), name='dsolist-detail'),
    path('list', DSOListListView.as_view(), name='dsolist-list'),
    path('observe', DSOObservationLogView.as_view(), name='dso-observed'),
    path('<int:pk>', DSODetailView.as_view(), name='dso-detail'),
)