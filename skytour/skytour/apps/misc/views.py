import datetime, pytz
from django.views.generic.dates import YearArchiveView
from .models import Calendar

class CalendarYearView(YearArchiveView):
    model = Calendar
    date_field = 'date'
    make_object_list = True
    allow_future = True
    template_name = 'calendar_archive_year.html'

    def get_context_data(self, **kwargs):
        context = super(CalendarYearView, self).get_context_data(**kwargs)
        context['event_list'] = Calendar.objects.order_by('date')
        return context