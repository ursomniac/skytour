from django.shortcuts import get_object_or_404
from django.urls import reverse, reverse_lazy
from django.views.generic import TemplateView
from django.views.generic.edit import UpdateView
from .models import *
from .forms import *

SUBMODEL_FORM_CLASSES = {
    'positive': SiteParameterPositiveIntegerForm,
    'string': SiteParameterStringForm,
    'number': SiteParameterNumberForm,
    'float': SiteParameterFloatForm,
    'link': SiteParameterLinkForm,
    'image': SiteParameterImageForm,
    'pdf': SiteParameterPDFForm
}
SUBMODEL_FORM_INSTANCES = {
    'positive': SiteParameterPositiveIntegerForm(),
    'string': SiteParameterStringForm(),
    'number': SiteParameterNumberForm(),
    'float': SiteParameterFloatForm(),
    'link': SiteParameterLinkForm(),
    'image': SiteParameterImageForm(),
    'pdf': SiteParameterPDFForm()
}

MODEL_CLASSES = {
    'positive': SiteParameterPositiveInteger,
    'string': SiteParameterString,
    'number': SiteParameterNumber,
    'float': SiteParameterFloat,
    'link': SiteParameterLink,
    'image': SiteParameterImage,
    'pdf': SiteParameterPDFFile
}
    
class SiteParameterListView(TemplateView):
    template_name = 'site_parameter_list.html'

    def get_context_data(self, **kwargs):
        context = super(SiteParameterListView, self).get_context_data(**kwargs)
        context['parameters'] = {
            'positive': SiteParameterPositiveInteger.objects.all(),
            'string': SiteParameterString.objects.all(),
            'number': SiteParameterNumber.objects.all(),
            'float': SiteParameterFloat.objects.all(),
            'link': SiteParameterLink.objects.all(),
            'image': SiteParameterImage.objects.all(),
            'pdf': SiteParameterPDFFile.objects.all()
        }
        return context

class SiteParameterEditView(UpdateView):
    template_name = 'form_parameter_edit.html'
    fields = ['value',]
    success_url = '/param/edit/result'
    
    def get_queryset(self):
        model = MODEL_CLASSES[self.kwargs['ptype']]
        pk = self.kwargs['pk']
        queryset = model.objects.filter(pk = pk)
        return queryset

    def get_object(self, queryset=None):
        ptype = self.kwargs['ptype']
        pk = self.kwargs['pk']
        object = MODEL_CLASSES[ptype].objects.get(pk=pk)
        print("20. OBJECT: ", object)
        print("21. VALUE: ", object.value)
        return get_object_or_404(MODEL_CLASSES[ptype], id=pk)

    def get_form_class(self):
        ptype = self.kwargs['ptype']
        form = SUBMODEL_FORM_CLASSES[ptype]
        print("10. GOT FORM CLASS: ", form)
        return form
    
    def form_invalid(self, form):
        print ("40. Invalid Form: ", form)
        print("41. Form Errors: ", form.errors)
        return super().form_invalid(form)
    
    def form_valid(self, form, **kwargs):
        print("30. Form: ", form)
        d = form.cleaned_data
        print("30. D: ", d)
        object = self.get_object()
        object.value = d['value']
        object.save()
        return super().form_valid(form)
    
    def post(self, request, *args, **kwargs):
        print("50. Got to post()")
        return super().post(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super(SiteParameterEditView, self).get_context_data(**kwargs)
        object = self.get_object()
        form_class = self.get_form_class()
        context['form'] = form_class(initial={'value': object.value})
        if self.request.POST:
            print("GOT POST")
        elif self.request.GET:
            print("GOT GET")
        else:
            print("GOT NOTHING?")
        print("91. GOT OBJECT: ", object)
        print("92. VALUE: ", object.value)
        print("93. TYPE: ", type(object.value))
        return context
    
class SiteParameterEditResultView(TemplateView):
    template_name = 'edit_parameter_result.html'

    def get_context_data(self, **kwargs):
        context = super(SiteParameterEditResultView, self).get_context_data(**kwargs)
        return context
    
class SiteParameterEditPositiveIntegerView(UpdateView):
    model = SiteParameterPositiveInteger
    template_name = 'form_parameter_edit.html'
    fields = ['value',]

    def get_success_url(self):
        success_url = reverse_lazy('param-edit-result') #, kwargs={'pk': self.object.pk})
        return success_url
