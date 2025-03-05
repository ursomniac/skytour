import datetime, pytz
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse, reverse_lazy
from django.utils.timezone import now
from django.views.generic.dates import YearArchiveView, MonthArchiveView
from django.views.generic import ListView, TemplateView
from django.views.generic.edit import UpdateView, DeleteView
from ..astro.calendar import create_calendar_grid, is_leap_year
from ..misc.models import TimeZone
from ..site_parameter.helpers import find_site_parameter
from .models import Calendar, Website, Glossary
from .forms import WebsiteAddForm, WebsiteEditForm, WebsiteDeleteForm

class CalendarYearView(YearArchiveView):
    """
    Generate a table (not a grid) for an entire year's Calendar entries
    """
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
    """
    Generate a grid for a month's Calendar entries
    """
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
        return context
    
class WebsiteListView(ListView):
    model = Website
    template_name = 'website_list.html'

    def get_context_data(self, **kwargs):
        context = super(WebsiteListView, self).get_context_data(**kwargs)
        context['create_form'] = WebsiteAddForm()
        return context
    
    def post(self, request, *args, **kwargs):
        form = WebsiteAddForm(request.POST)
        if form.is_valid():
            d = form.cleaned_data
            obj = Website()
            obj.name = d['name']
            obj.url = d['url']
            obj.save()
        return self.get(request, *args, **kwargs)
    
class WebsiteEditView(UpdateView):
    template_name = 'form_website_edit.html'
    model = Website
    form_class = WebsiteEditForm
    success_url = reverse_lazy('website-edit-result')

class WebsiteDeleteView(DeleteView):
    template_name = 'form_website_delete.html'
    model = Website
    form_class = WebsiteDeleteForm
    success_url = reverse_lazy('website-delete-result')

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.pk = self.object.pk
        self.object.delete()
        return HttpResponseRedirect('misc/website/removed/result')

class WebsiteEditResultView(TemplateView):
    template_name = 'edit_website_result.html'

class WebsiteDeleteResultView(TemplateView):
    template_name = 'delete_website_result.html'

class GlossaryListView(ListView):
    model = Glossary
    template_name = 'glossary_list.html'

    def get_context_data(self, **kwargs):
        context = super(GlossaryListView, self).get_context_data(**kwargs)
        return context