from django.urls import path
from .views import (
    BrightStarDetailView, 
    BrightStarListView, 
)

urlpatterns = (
    path('', BrightStarListView.as_view(), name='star-list'),
    path('<int:pk>', BrightStarDetailView.as_view(), name='star-detail'),
)