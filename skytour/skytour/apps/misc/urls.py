from django.urls import path
from .views import (
    CalendarYearView
)

urlpatterns = (
    path('<int:year>/', CalendarYearView.as_view(), name='calendar=year'),
)