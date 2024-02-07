from django.views.generic.base import TemplateView
from django.views.generic.detail import DetailView
from django.views.generic.edit import FormView
from django.views.generic.list import ListView
from .models import TargetDSO, TargetObservingMode

class TargetListView(ListView):
    model = TargetDSO
    template_name = 'target_list.html'

    def get_context_data(self, **kwargs):
        context = super(TargetListView, self).get_context_data(**kwargs)
        con_filter = self.request.GET.get('con', None)
        todo_filter = self.request.GET.get('done', False)
        if con_filter:
            context['object_list'] = context['object_list'].filter(dso__constellation__abbreviation=con_filter)
        if todo_filter:
            context['object_list'] = context['object_list'].filter(ready_to_go=False)
        return context
    
class TargetDetailView(DetailView):
    model = TargetDSO
    template_name = 'target_detail.html'

    def get_context_data(self, **kwargs):
        context = super(TargetDetailView, self).get_context_data(**kwargs)
        obj = self.get_object()
        mode_dict = {}
        for mode in obj.targetobservingmode_set.all():
            mode_dict[mode.mode] = mode
        mode_set = []
        for my_mode in 'NBSMI':
            if my_mode in obj.mode_list:
                mode_set.append(mode_dict[my_mode])
        context['mode_list'] = mode_set
        return context