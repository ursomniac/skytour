from django.urls import path
from .views import (
    BrightStarDetailView, 
    BrightStarListView, 
    SkyView
)

urlpatterns = (
    path('skyview', SkyView.as_view(), name='skymap-detail'),
    path('', BrightStarListView.as_view(), name='star-listing'),
    path('<int:pk>', BrightStarDetailView.as_view(), name='star-detail'),
)