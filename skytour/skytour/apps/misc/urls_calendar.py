from django.urls import path
from .views import (
    CalendarYearView, CalendarMonthView,
    CalendarAddItemView, CalendarUpdateItemView
)

urlpatterns = (
    path('', CalendarMonthView.as_view(), name='calendar-current'),
    path('<int:year>/', CalendarYearView.as_view(), name='calendar-year'),
    path('<int:year>/<str:month>', CalendarMonthView.as_view(), name='calendar-month'),
    path('add', CalendarAddItemView.as_view(), name='calendar-add'),
    path('edit/<int:pk>', CalendarUpdateItemView.as_view(), name='calendar-edit'),
)