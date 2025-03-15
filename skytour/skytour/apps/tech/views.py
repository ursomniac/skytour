from django.urls import reverse
from django.views.generic import TemplateView
from django.views.generic.list import ListView
from django.views.generic.edit import UpdateView, DeleteView
from .forms import TelescopeForm, TelescopeDeleteForm
from .models import Telescope

class TelescopeListView(ListView):
    model = Telescope
    template_name = 'telescope_list.html'

    def post(self, request, *args, **kwargs):
        form = TelescopeForm(request.POST)
        if form.is_valid():
            d = form.cleaned_data
            obj = Telescope()
            obj.name = d['name']
            obj.aperture = d['aperture']
            obj.focal_length = d['focal_length']
            obj.order_in_list = d['order_in_list']
            obj.active = d['active']
            obj.is_default = d['is_default']
            obj.save()
        return self.get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(TelescopeListView, self).get_context_data(**kwargs)
        context['create_form'] = TelescopeForm()
        return context

class TelescopeUpdateView(UpdateView):
    model = Telescope
    template_name = 'telescope_edit.html'
    success_url = '/tech/telescope/edit/result'
    form_class = TelescopeForm

class TelescopeDeleteView(DeleteView):
    template_name = 'telescope_delete.html'
    model = Telescope
    success_url = '/tech/telescope/delete/result'

    def get_context_data(self, **kwargs):
        context = super(TelescopeDeleteView, self).get_context_data()
        context['form'] = TelescopeDeleteForm()
        return context

class TelescopeEditResultView(TemplateView):
    template_name = 'telescope_edit_result.html'

class TelescopeDeleteResultView(TemplateView):
    template_name = 'telescope_delete_result.html'
