from django.db import transaction
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django.views.generic import TemplateView
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from django.views.generic.edit import UpdateView, CreateView, DeleteView

from ..session.mixins import CookieMixin
from ..site_parameter.helpers import find_site_parameter
from .forms import (
    NewObservingLocationForm, 
    ObservingLocationAddMaskFormset, 
    ObservingLocationUpdateMaskFormset,
    ObservingLocationDeleteForm
)
from .models import ObservingLocation
from .plot import make_location_plot, plot_sqm_history, plot_expect_vs_observed_sqm

class ObservingLocationListView(CookieMixin, ListView):
    model = ObservingLocation
    template_name = 'observing_location_list.html'

    def get_context_data(self, **kwargs):
        context = super(ObservingLocationListView, self).get_context_data(**kwargs)
        max_distance = find_site_parameter('max-location-distance', 60., 'float')
        all_locations = ObservingLocation.objects.all()

        sections = ['Active', 'Provisional', 'Possible', 'Issues', 'TBD', 'Distant', 'Rejected']
        locations = {}
        for s in sections:
            if s == 'Distant':
                locations[s] = all_locations.filter(travel_distance__gte=max_distance).exclude(status='Active')
            elif s != 'Active':
                    locations[s] = all_locations.filter(status=s).exclude(travel_distance__gt=max_distance)
            else:
                locations[s] = all_locations.filter(status=s)
        context['locations'] = locations
        context['sections'] = sections
        reversed = context['color_scheme'] == 'dark'

        plot_locations = all_locations.exclude(travel_distance__gte=max_distance)
        context['sqm_plot'] = make_location_plot(plot_locations, 'sqm', reversed=reversed)
        context['brightness_plot'] = make_location_plot(plot_locations, 'bright', reversed=reversed)
        context['bortle_plot'] = plot_expect_vs_observed_sqm(all_locations, reversed=reversed)
        context['table_id'] = 'location_table'
        return context

class ObservingLocationDetailView(CookieMixin, DetailView):
    model = ObservingLocation
    template_name = 'observing_location_detail.html'

    def get_context_data(self, **kwargs):
        context = super(ObservingLocationDetailView, self).get_context_data(**kwargs)
        location = self.get_object()
        reversed = context['color_scheme'] == 'dark'
        context['sqm_plot'] = plot_sqm_history(location, reversed=reversed)
        return context
    
class ObservingLocationAddView(CreateView):
    model = ObservingLocation
    template_name = 'form_add_new_location.html'
    form_class = NewObservingLocationForm

    def form_valid(self, form):
        context = self.get_context_data()
        children = context['mask_formset']
        with transaction.atomic():
            self.object = form.save()
            if children.is_valid():
                children.instance = self.object
                children.save()
            else:
                print("CHILDREN INVALID")
                print("ERRORS: ", children.errors)
        #return self.get(self.request)
        return HttpResponseRedirect(self.object.get_absolute_url())    
    
    def form_invalid(self, form):
        return self.get(self.request)
    
    def formset_valid(self, formset):
        for form in formset:
            if form.has_changed(): # only save form if it is not empty
                form.save()
        return super().form_valid(formset)

    def get_context_data(self, **kwargs):
        context = super(ObservingLocationAddView, self).get_context_data(**kwargs)
        context['op'] = 'Add'
        if self.request.POST:
            mask_formset = ObservingLocationAddMaskFormset(self.request.POST)
        else:
            mask_formset = ObservingLocationAddMaskFormset(instance=self.object)
        context['mask_formset'] = mask_formset
        return context

class ObservingLocationUpdateView(UpdateView):
    model = ObservingLocation
    template_name = 'form_add_new_location.html'
    form_class = NewObservingLocationForm

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form()
        mask_formset = ObservingLocationUpdateMaskFormset(request.POST, instance=self.object)
        if form.is_valid() and mask_formset.is_valid():
            return self.form_valid(form, mask_formset)
        else:
            return self.form_invalid(form, mask_formset)
        
    def form_valid(self, form, mask_formset):
        pk = self.get_object().pk
        form.save()
        mask_formset.save()
        return redirect('observing-location-detail', pk=pk)
    
    def form_invalid(self, form, mask_formset):
        print("FORM IS INVALID")
        print("FORM ERRORS:", form.errors)
        print("MASK FORM ERRORS: ", mask_formset.errors)
        return self.render_to_response(self.get_context_data(form=form, mask_formset=mask_formset))

    def formset_valid(self, formset):
        for form in formset:
            if form.has_changed(): # only save form if it is not empty
                form.save()
        return super().form_valid(formset)

    def get_context_data(self, **kwargs):
        context = super(ObservingLocationUpdateView, self).get_context_data(**kwargs)
        context['op'] = 'Edit'
        if self.request.POST:
            mask_formset = ObservingLocationUpdateMaskFormset(self.request.POST)
        else:
            mask_formset = ObservingLocationUpdateMaskFormset(instance=self.object)
        context['parent_pk'] = self.get_object().pk
        context['mask_formset'] = mask_formset
        return context
    
class ObservingLocationDeleteView(DeleteView):
    model = ObservingLocation
    success_url = '/observing_location/delete/result'
    template_name = 'location_delete.html'

    def get_context_data(self, **kwargs):
        context = super(ObservingLocationDeleteView, self).get_context_data()
        context['form'] = ObservingLocationDeleteForm()
        return context
    
class ObservingLocationDeleteResultView(TemplateView):
    template_name = 'location_delete_result.html'