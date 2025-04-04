import datetime, pytz
from django.db import transaction
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.utils.text import slugify
from django.utils.timezone import now
from django.views.generic.dates import YearArchiveView, MonthArchiveView
from django.views.generic import ListView, TemplateView
from django.views.generic.edit import UpdateView, DeleteView, CreateView
from ..astro.calendar import create_calendar_grid, is_leap_year
from ..observe.models import ObservingLocation
from .models import Calendar, Website, Glossary, PDFManual
from .forms import (
    WebsiteAddForm, WebsiteEditForm, WebsiteDeleteForm,
    PDFManualAddForm, PDFManualEditForm, PDFManualDeleteForm,
    CalendarAddEventReferenceFormset,
    CalendarEditEventReferenceFormset
)

MONTHS = [
    (1, 'January', 'Jan'), (2, 'February', 'Feb'), (3, 'March', 'Mar'),
    (4, 'April', 'Apr'), (5, 'May', 'May'), (6, 'June', 'Jun'),
    (7, 'July', 'Jul'), (8, 'August', 'Aug'), (9, 'September', 'Sep'),
    (10, 'October', 'Oct'), (11, 'November', 'Nov'), (12, 'December', 'Dec')
]

class CalendarYearView(YearArchiveView):
    """
    Generate a table (not a grid) for an entire year's Calendar entries
    """
    model = Calendar
    date_field = 'date'
    make_object_list = True
    allow_future = True
    template_name = 'calendar_archive_year.html'

    def get_allow_future(self):
        return True
    
    def get_allow_empty(self):
        return True

    def get_context_data(self, **kwargs):
        context = super(CalendarYearView, self).get_context_data(**kwargs)
        this_year = context['year'] = self.kwargs['year']
        context['event_list'] = Calendar.objects.order_by('date')
        context['months'] = MONTHS

        # Generate list of years for form
        context['last_year'] = this_year - 1
        context['next_year'] = this_year + 1
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
        month_list = [None, 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
            'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'
        ]
        context = super(CalendarMonthView, self).get_context_data(**kwargs)
        context['event_list'] = Calendar.objects.order_by('date')
        this_date = context['month'] # defined in super()
        this_month = this_date.month
        this_year = this_date.year

        # Generate list of years for form
        all = Calendar.objects.order_by('-date', '-time')
        oldest_year = all.last().date.year
        latest_year = all.first().date.year
        year_list = list(range(oldest_year, latest_year + 1))[::-1]

        context['year_list'] = year_list
        context['month_list'] = month_list[1:]
        context['form_year'] = this_year
        context['form_month'] = month_list[this_month]
        
        start_date = datetime.datetime(this_year, this_month, 1, 0, 0).replace(tzinfo=pytz.utc)
        days_out = 29 if this_month == 2 and is_leap_year(this_year) else out[this_month]

        # TODO: Figure out how to localize for DST
        my_time_zone = pytz.timezone(ObservingLocation.get_default_location().time_zone.pytz_name)

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

class PDFManualListView(ListView):
    model = PDFManual
    template_name = 'pdfmanual_list.html'

    def get_context_data(self, **kwargs):
        context = super(PDFManualListView, self).get_context_data(**kwargs)
        context['create_form'] = PDFManualAddForm()
        return context
    
    def post(self, request, *args, **kwargs):
        form = PDFManualAddForm(request.POST, request.FILES)
        if form.is_valid():
            d = form.cleaned_data
            if d['op'] != 'delete':
                obj = PDFManual()
                obj.title = d['title']
                obj.slug = slugify(obj.title)
                obj.pdf_file = d['pdf_file']
                obj.save()
        else:
            print("ERROR WITH FORM: ", form)
            print("FORM ERRORS: ", form.errors)
        return self.get(request, *args, **kwargs)
    
class PDFManualEditView(UpdateView):
    template_name = 'form_manual_edit.html'
    model = PDFManual
    form_class = PDFManualEditForm
    success_url = reverse_lazy('manual-edit-result')

    def get_context_data(self, **kwargs):
        context = super(PDFManualEditView, self).get_context_data(**kwargs)
        return context

class PDFManualEditResultView(TemplateView):
    template_name = 'edit_manual_result.html'

class PDFManualDeleteView(DeleteView):
    template_name = 'form_manual_delete.html'
    model = PDFManual
    form_class = PDFManualDeleteForm
    success_url = reverse_lazy('manual-delete-result')

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.pk = self.object.pk
        self.object.delete()
        return HttpResponseRedirect('misc/manual/delete/result')

class PDFManualDeleteResultView(TemplateView):
    template_name = 'edit_manual_result.html'

class CalendarAddItemView(CreateView):
    model = Calendar
    template_name = 'add_calendar_item.html'
    fields = ['date', 'time', 'title', 'description', 'event_type',]

    def xpost(self, request, *args, **kwargs):
        print(request.POST)
        return self.get(request, *args, **kwargs)
    
    def form_valid(self, form):
        context = self.get_context_data()
        children = context['ref_formset']
        with transaction.atomic():
            self.object = form.save()
            if children.is_valid():
                children.instance = self.object
                children.save()
        return self.get(self.request)
    
    def form_invalid(self, form):
        return self.get(self.request)

    def get_context_data(self, **kwargs):
        context = super(CalendarAddItemView, self).get_context_data(**kwargs)
        context['year'] = datetime.datetime.now().year
        context['op'] = 'Add'
        if self.request.POST: 
            ref_formset = CalendarAddEventReferenceFormset(self.request.POST)
        else:
            ref_formset = CalendarAddEventReferenceFormset()
        context['ref_formset'] = ref_formset
        return context
    
class CalendarUpdateItemView(UpdateView):
    model = Calendar
    template_name = 'update_calendar_item.html'
    fields = ['date', 'time', 'title', 'description', 'event_type',]

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form()
        ref_formset = CalendarEditEventReferenceFormset(request.POST, instance=self.object)
        if form.is_valid() and ref_formset.is_valid():
            return self.form_valid(form, ref_formset)
        else:
            return self.form_invalid(form, ref_formset)
        
    def form_valid(self, form, ref_formset):
        d = form.cleaned_data
        year = d['date'].year
        form.save()
        ref_formset.save()
        return redirect('calendar-year', year=year)
    
    def form_invalid(self, form, ref_formset): 
        print("FORM IS INVALID")
        print("FORM ERRORS: ", form.errors)
        print("REF FORM ERRORS: ", ref_formset.errors)
        return self.render_to_response(self.get_context_data(form=form, ref_formset=ref_formset))

    def get_context_data(self, **kwargs):
        context = super(CalendarUpdateItemView, self).get_context_data(**kwargs)
        context['year'] = datetime.datetime.now().year
        context['op'] = 'Update'
        object = self.get_object()
        context['parent_pk'] = object.pk
        if self.request.POST: 
            ref_formset = CalendarEditEventReferenceFormset(self.request.POST)
        else:
            ref_formset = CalendarEditEventReferenceFormset(instance=self.object)
        context['ref_formset'] = ref_formset
        return context