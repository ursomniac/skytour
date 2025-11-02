from django.urls import path
from .views import (
    ObservableVariableStarListView,
    VariableStarDetailView
)

urlpatterns = (
    path('', ObservableVariableStarListView.as_view(), name='obsvar-list'),
    path('<str:id_in_catalog>', VariableStarDetailView.as_view(), name='obsvar-detail'),
    #path('gcvs', GCVSListView.as_view(), name='gcvs-list'),
)