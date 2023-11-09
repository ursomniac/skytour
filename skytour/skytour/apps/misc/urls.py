from django.urls import path
from .views import (
    CalendarYearView, CalendarMonthView
)

urlpatterns = (
    path('', CalendarMonthView.as_view(), name='calendar-current'),
    path('<int:year>/', CalendarYearView.as_view(), name='calendar=year'),
    path('<int:year>/<str:month>', CalendarMonthView.as_view(), name='calendar-month')
)