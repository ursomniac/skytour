from collections import Counter
from django.views.generic.base import TemplateView
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from .models import DSO, PRIORITY_CHOICES

class DSOListView(ListView):
    model = DSO
    template_name = 'dso_list.html'
    context_object_name = 'dso_list'
    paginate_by = 100

    def get_context_data(self, **kwargs):
        context = super(DSOListView, self).get_context_data(**kwargs)
        context['table_id'] = 'dso_list'
        return context

class DSODetailView(DetailView):
    model = DSO 
    template_name = 'dso_detail.html'

    def get_context_data(self, **kwargs):
        context = super(DSODetailView, self).get_context_data(**kwargs)
        return context

class PriorityListView(TemplateView):
    template_name = 'priority_list.html'

    def get_context_data(self, **kwargs):
        context = super(PriorityListView, self).get_context_data(**kwargs)
        context['priorities'] = [x[0] for x in PRIORITY_CHOICES]
        dso_priorities = list(DSO.objects.values_list('priority', flat=True))
        context['priority_count'] = dict(Counter(dso_priorities))
        context['table_id'] = 'priority_list'
        return context

class PriorityDetailView(TemplateView):
    template_name = 'priority_detail.html'

    def get_context_data(self, **kwargs):
        context = super(PriorityDetailView, self).get_context_data(**kwargs)
        context['priority'] = priority = self.kwargs['priority']
        context['dso_list'] = DSO.objects.filter(priority=priority)
        context['hide_priority'] = True
        context['table_id'] = 'dso_list_by_priority'
        return context

