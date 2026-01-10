from django.urls import path
from .views import (
    BrightStarDetailView, 
    BrightStarListView, 
    SkyView,
    ZenithMagView,
    ZenithMagResult
)

urlpatterns = (
    path('skyview', SkyView.as_view(), name='skymap-detail'),
    path('zenith', ZenithMagView.as_view(), name='zenith-view'),
    path('zenith/result', ZenithMagResult.as_view(), name='zenith-result'),
    path('hr/', BrightStarListView.as_view(), name='bright-star-listing'),
    path('hr/<int:pk>', BrightStarDetailView.as_view(), name='bright-star-detail'),
)