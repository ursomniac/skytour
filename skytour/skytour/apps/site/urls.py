from django.urls import path
from .views import HomePageView, TodayPageView

urlpatterns = (
    path('', HomePageView.as_view(), name='home'),
    path('events', TodayPageView.as_view(), name='today')
)