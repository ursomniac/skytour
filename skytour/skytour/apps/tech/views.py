from django.views.generic import TemplateView
from django.views.generic.list import ListView
from django.views.generic.edit import UpdateView, DeleteView
from .forms import (
    TelescopeForm, TelescopeDeleteForm,
    EyepieceForm, EyepieceDeleteForm,
    EyepieceFilterForm, EyepieceFilterDeleteForm
)
from .models import Telescope, Eyepiece, Filter

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

class EyepieceListView(ListView):
    model = Eyepiece
    template_name = 'eyepiece_list.html'
    
    #fields = ['type', 'focal_length', 'apparent_fov', 'short_name', 'telescope']
    def post(self, request, *args, **kwargs):
        form = EyepieceForm(request.POST)
        if form.is_valid():
            d = form.cleaned_data
            obj = Eyepiece()
            obj.type = d['type']
            obj.focal_length = d['focal_length']
            obj.apparent_fov = d['apparent_fov']
            obj.short_name = d['short_name']
            obj.telescope_id = d['telescope'].pk
            obj.save()
        return self.get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(EyepieceListView, self).get_context_data(**kwargs)
        create_form = EyepieceForm()
        context['create_form'] = create_form 
        return context

class EyepieceUpdateView(UpdateView):
    model = Eyepiece
    template_name = 'eyepiece_edit.html'
    success_url = '/tech/eyepiece/edit/result'
    form_class = EyepieceForm

class EyepieceDeleteView(DeleteView):
    template_name = 'eyepiece_delete.html'
    model = Eyepiece
    success_url = '/tech/eyepiece/delete/result'

    def get_context_data(self, **kwargs):
        context = super(EyepieceDeleteView, self).get_context_data()
        context['form'] = EyepieceDeleteForm()
        return context

class EyepieceEditResultView(TemplateView):
    template_name = 'eyepiece_edit_result.html'

class EyepieceDeleteResultView(TemplateView):
    template_name = 'eyepiece_delete_result.html'

class FilterListView(ListView):
    model = Filter
    template_name = 'filter_list.html'

    """
            fields = [
            'name', 'short_name', 'filter_type', 
            'central_wavelength', 'fwhm', 'dominant_wavelength',
            'transmission', 
            'transmission_curve', 'watten_curve',
            'notes', 'tech_notes'
        ]
    """
    def post(self, request, *args, **kwargs):
        form = EyepieceFilterForm(request.POST, request.FILES)
        if form.is_valid():
            d = form.cleaned_data
            obj = Filter()
            obj.name = d['name']
            obj.short_name = d['short_name']
            obj.filter_type = d['filter_type']
            obj.central_wavelength = d['central_wavelength']
            obj.fwhm = d['fwhm']
            obj.dominant_wavelength = d['dominant_wavelength']
            obj.transmission = d['transmission']
            obj.notes = d['notes']
            obj.tech_notes= d['tech_notes']
            obj.transmission_curve = d['transmission_curve']
            obj.watten_curve = d['watten_curve']
            obj.save()
        else:
            print("FORM IS INVALID")
            print(form.errors)
        return self.get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(FilterListView, self).get_context_data(**kwargs)
        create_form = EyepieceFilterForm()
        context['create_form'] = create_form 
        return context
    
class FilterUpdateView(UpdateView):
    model = Filter
    template_name = 'filter_edit.html'
    success_url = '/tech/filter/edit/result'
    form_class = EyepieceFilterForm

class FilterDeleteView(DeleteView):
    template_name = 'filter_delete.html'
    model = Filter
    success_url = '/tech/filter/delete/result'

    def get_context_data(self, **kwargs):
        context = super(FilterDeleteView, self).get_context_data()
        context['form'] = EyepieceFilterDeleteForm()
        return context

class FilterEditResultView(TemplateView):
    template_name = 'filter_edit_result.html'

class FilterDeleteResultView(TemplateView):
    template_name = 'filter_delete_result.html'