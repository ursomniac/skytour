import datetime, pytz
from django.http import Http404
from django.utils.timezone import now
from django.views.generic.dates import YearArchiveView, MonthArchiveView
from ..astro.calendar import create_calendar_grid, is_leap_year
from ..misc.models import TimeZone
from ..site_parameter.helpers import find_site_parameter
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
    
class CalendarMonthView(MonthArchiveView):
    model = Calendar
    date_field = 'date'
    make_object_list = True
    allow_future = True
    template_name = 'calendar_archive_month.html'

    def get_allow_future(self):
        return True
    
    def get_allow_empty(self):
        return True

    def get_month(self):
        form_month = self.request.GET.get('month', None)
        try:
            month = super(CalendarMonthView, self).get_month()
        except Http404:
            month = now().strftime(self.get_month_format())
        return form_month if form_month else month
    
    def get_year(self):
        form_year = self.request.GET.get('year', None)
        try:
            year = super(CalendarMonthView, self).get_year()
        except Http404:
            year = now().strftime(self.get_year_format())
        return int(form_year) if form_year else year

    def get_context_data(self, **kwargs):
        out = [0, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
        context = super(CalendarMonthView, self).get_context_data(**kwargs)
        context['event_list'] = Calendar.objects.order_by('date')
        
        this_date = context['month'] # defined in super()
        this_month = this_date.month
        this_year = this_date.year

        start_date = datetime.datetime(this_year, this_month, 1, 0, 0).replace(tzinfo=pytz.utc)
        days_out = 29 if this_month == 2 and is_leap_year(this_year) else out[this_month]
        time_zone_id = find_site_parameter('default-time-zone-id', 2, 'positive')
        my_time_zone = pytz.timezone(TimeZone.objects.get(pk=time_zone_id).name)
        grid = create_calendar_grid(start_date, days_out=days_out - 1, time_zone=my_time_zone)
        context['grid'] = grid

        # Get around Next Month being None - sigh
        """
        if context['next_month'] is None:
            ty = int(context['month'].year)
            tm = int(context['month'].month)
            td = int(context['month'].day) # always 1
            tm += 1
            if tm > 12:
                tm = tm % 12
                ty += 1
            context['next_month'] = datetime.date(ty, tm, td)
        else:
            print("NEXT TYPE: ", type(context['next_month']))
        print ("THIS: ", context['month'])            
        print ("NEXT: ", context['next_month'])
        """
        
        return context