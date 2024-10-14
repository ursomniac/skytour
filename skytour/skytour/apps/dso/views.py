import datetime as dt
from collections import Counter
from dateutil.parser import isoparse
from django.db.models import Q, Count
from django.core.paginator import Paginator
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django.urls import reverse
from django.views.generic.base import TemplateView, View
from django.views.generic.detail import DetailView
from django.views.generic.edit import FormView
from django.views.generic.list import ListView
from reportlab.pdfgen import canvas
from ..abstract.utils import get_real_time_conditions
from ..astro.culmination import get_opposition_date_at_time
from ..session.mixins import CookieMixin
from ..site_parameter.helpers import find_site_parameter
from ..utils.timer import compile_times
from .atlas_utils import find_neighbors, assemble_neighbors
from .finder import create_dso_finder_chart, plot_dso_list
from .forms import DSOFilterForm, DSOAddForm
from .geo import get_circle_center
from .helpers import get_map_parameters, get_star_mag_limit
from .models import DSO, DSOList, AtlasPlate, DSOAlias, DSOInField, DSOImagingChecklist
from .observing import make_observing_date_grid, get_max_altitude
from .search import search_dso_name, find_cat_id_in_string
from .utils import select_atlas_plate, select_other_atlas_plates
from .utils_checklist import checklist_form, checklist_params, create_new_observing_list, \
    filter_dsos, get_filter_params, update_dso_filter_context
from .vocabs import PRIORITY_CHOICES

class DSOListView(ListView):
    model = DSO
    template_name = 'dso_list.html'
    context_object_name = 'dso_list'
    paginate_by = 100

    def get_queryset(self):
        queryset = super().get_queryset()
        params = get_filter_params(self.request)
        return queryset

    def get_context_data(self, **kwargs):
        context = super(DSOListView, self).get_context_data(**kwargs)
        params = get_filter_params(self.request)
        context = update_dso_filter_context(context, params)
        dso_list = filter_dsos(params, DSO.objects.all())
        context['total_returned'] = len(dso_list)
        context['default_dec_limit'] = dec_limit = find_site_parameter('declination-limit', -30, 'float')
        # Pagination
        page_no = self.request.GET.get('page', 1)
        num_on_page = self.request.GET.get('page_size', self.paginate_by)
        context['num_on_page'] = num_on_page
        p = Paginator(dso_list, num_on_page)
        this_page = p.page(page_no)
        context['page_obj'] = this_page
        context['dso_list'] = this_page.object_list # Just this page of objects.
        context['is_paginated'] = True
        # context['dso_count'] = len(context['dso_list'])
        context['table_id'] = 'dso_list'
        return context

class DSODetailView(CookieMixin, DetailView):
    model = DSO 
    template_name = 'dso_detail.html'

    def get_context_data(self, **kwargs):
        context = super(DSODetailView, self).get_context_data(**kwargs)
        object = self.get_object()
        now = self.request.GET.get('now', False)
        location = context['location']
        local_dt = isoparse(context['local_time_start'])
        context['local_dt_str'] = local_dt.strftime("%Ih%Mm %p")
        context['max_altitude'] = get_max_altitude(object, location=location)
        context['observing_date_grid'] = make_observing_date_grid(object)
        context['image_list'] = self.object.images.order_by('order_in_list')
        context['other_library_images'] = self.object.image_library.all() # [1:]
        context['library_slideshow'] = self.object.image_library.filter(use_in_carousel=1).order_by('order_in_list')
        context['map_slideshow'] = self.object.map_image_list
        context['finder_slideshow'] = self.object.finder_image_list
        context['other_metadata'] = self.object.other_metadata_text
        context['other_parameters'] = self.object.other_parameters
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

class DSOListListView(CookieMixin, ListView):
    model = DSOList
    template_name = 'dsolist_list.html'

class DSOListDetailView(CookieMixin, DetailView):
    model = DSOList
    template_name = 'dsolist_detail.html'

    def get_context_data(self, **kwargs):
        context = super(DSOListDetailView, self).get_context_data(**kwargs)
        object = self.get_object()
        # Make a map
        dso_list = self.object.dso.all()
        mag =  2.4 if not object.map_scaling_factor else object.map_scaling_factor
        center_ra, center_dec, max_dist = get_circle_center(dso_list)
        #print(f"RA: {center_ra} DEC: {center_dec}  MD: {max_dist}")
        if (max_dist is None or max_dist < 0.001)  and center_ra is not None:
            max_dist = 5.
        if max_dist is not None and max_dist > 0.:
            fov = max_dist * 1.2

            star_mag_limit = get_star_mag_limit(max_dist)

            map = plot_dso_list(
                center_ra, 
                center_dec,
                dso_list,
                fov=fov,
                star_mag_limit = star_mag_limit,
                reversed = False,
                label_size='small',
                symbol_size=60,
                title = f"DSO List: {self.object.name}"
            )
            context['map'] = map
        context['table_id'] = 'dsos-on-list'
        return context

class DSOFilterView(FormView):
    form_class = DSOFilterForm
    template_name = 'dso_filter.html'

    def form_valid(self, form, **kwargs):
        context = self.get_context_data(**kwargs)
        d = form.cleaned_data
        context['values'] = d
        context['completed'] = True

        dso_list = DSO.objects.exclude(priority='None')
        # Filter on RA, DEC
        if d['ra_min'] is not None and d['ra_max'] is not None:
            if d['ra_min'] > d['ra_max']: # crosses 0h
                dso_list = dso_list.filter(Q(ra__gte=d['ra_min']) | Q(ra__lte=d['ra_max']))
            else:
                dso_list = dso_list.filter(ra__gte=d['ra_min'], ra__lte=d['ra_max'])
        if d['dec_min'] is not None and d['dec_max'] is not None:
            dso_list = dso_list.filter(dec__gte=d['dec_min'], dec__lte=d['dec_max'])
        if d['object_type'].count() > 0:
            dso_list = dso_list.filter(object_type__in=d['object_type'])
        if len(d['priority']) > 0:
            dso_list = dso_list.filter(priority__in=d['priority'])
        if d['mag_max'] is not None:
            dso_list = dso_list.exclude(magnitude__gte=d['mag_max'])
        if d['surface_max'] is not None:
            dso_list = dso_list.exclude(surface_brightness__gte=d['surface_max'])
        if d['filter_imaged']:
            unimaged_ids = [d.pk for d in dso_list if d.num_library_images == 0]
            dso_list = DSO.objects.filter(pk__in=unimaged_ids)
        context['dso_count'] = dso_list.count()
        context['dso_found'] = dso_list.order_by('ra')
        context['add_form'] = DSOAddForm(dso_list)
        context['table_id'] = 'dso_picker'
        return self.render_to_response(context)

class DSOCreateList(TemplateView):

    def post(self, request):
        if request.method == 'POST':
            add_dso_list = request.POST.getlist('add_dso')
            list_instance = request.POST['dso_list']
            new_list = request.POST['new_dso_list']
            new_description = request.POST['new_dso_description']

            error = False
            if new_list is not None and new_list.strip() != '':
                dso_list = DSOList()
                dso_list.name = new_list
                dso_list.description = new_description
                dso_list.save()
                current_set = dso_list.dso.all() 

            elif list_instance is not None and list_instance.strip() != '':
                dso_list = DSOList.objects.filter(pk=int(list_instance)).first()
                if dso_list is None: # Didn't find the list... how?
                    error = True
                else:
                    current_set = dso_list.dso.all()

            else: # start over!  neither selecting or adding a DSOList instance
                error = True

            if error:
                return HttpResponseRedirect('/dso/filter')

            # Update the list of DSOs to the list.
            for dso in add_dso_list:
                pk = int(dso)
                exists = current_set.filter(pk = pk).first()
                if exists is None:
                    dso_to_add = DSO.objects.filter(pk = pk).first()
                    if dso_to_add is not None:
                        dso_list.dso.add(dso_to_add)
                        
        return HttpResponseRedirect(reverse('dsolist-detail', args=[dso_list.pk]))

class AtlasPlateListView(ListView):
    model = AtlasPlate
    template_name = 'atlasplate_list.html'

    def get_context_data(self, **kwargs):
        context = super(AtlasPlateListView, self).get_context_data(**kwargs)
        all_plates = AtlasPlate.objects.all()
        d = {}
        context['head'] = range(24)
        dlist = [
            (90, 1), (75, 12), (60, 16), (45, 20), (30, 24), (15, 32), (0, 48),
            (-15, 32), (-30, 24), (-45, 20), (-60, 16), (-75, 12), (-90, 1)
        ]
        n = 0
        for key, np in dlist:
            col = int(480 / np)  # colspan for each
            plates = []            
            for p in range(np):
                n += 1
                obj = all_plates.filter(plate_id=n).first()
                this_plate = dict(
                    ra = f"{p * 24/np:.1f}",
                    number = n,
                    slug = f"{n}",
                    title = obj.plate_title
                )
                plates.append(this_plate)
            d[key] = dict(
                plates=plates,
                cspan = col
            )
        context['plate_list'] = d
        return context

class AtlasPlateDetailView(CookieMixin, DetailView):
    model = AtlasPlate
    template_name = 'atlasplate_detail.html'

    def get_context_data(self, **kwargs):
        context = super(AtlasPlateDetailView, self).get_context_data(**kwargs)
        obj = self.get_object()
        context['table_id'] = f"atlas_dso_{obj.plate_id}"
        context['selected_atlas_plate'] = select_atlas_plate(obj.plate_images, context)
        context['other_atlas_plates'] = select_other_atlas_plates(obj.plate_images, context['selected_atlas_plate'])
        neighbors = find_neighbors(obj.center_ra, obj.center_dec)
        context['assembled_neighbors'] = assemble_neighbors(neighbors)
        return context

class DSOObservationLogView(CookieMixin, ListView):
    model = DSO
    template_name = 'dsoobservation_list.html'

    def get_context_data(self, **kwargs):
        context = super(DSOObservationLogView, self).get_context_data(**kwargs)
        context['dso_list'] = DSO.objects.annotate(nobs=Count('observations')).filter(nobs__gt=0).order_by('-nobs')
        context['dso_table'] = 'dsos-observed'
        return context
    
class DSOChecklistView(ListView):
    model = DSOImagingChecklist
    template_name = 'imaging_checklist.html'

    def get_context_data(self, **kwargs):
        context = super(DSOChecklistView, self).get_context_data(**kwargs)
        # Deal with form
        form_params = checklist_params(self.request)
        # print ("FORM PARAMS: ", form_params)
        all_dsos = DSOImagingChecklist.objects.all()
        
        #context['seen'] = 'checked' if form_params['seen'] else ''
        context['priority'] = form_params['priority']
        context['dso_type'] = form_params['dso_type'] if form_params['dso_type'] != 'all' else ''
        context['constellation'] = form_params['constellation'] if form_params['constellation'] else ''
        context['subset'] = form_params['subset'] if form_params['subset'] else 'all'
        context['exclude_issues'] = form_params['exclude_issues']
        context['dso_list'] = checklist_form(form_params, all_dsos)
        context['list_count'] = context['dso_list'].count()
        context['show_map'] = form_params['show_map']
        new_obs_list = None
        if form_params['create_list']:
            new_obs_list = create_new_observing_list(context['dso_list'], form_params)
        context['new_obs_list'] = new_obs_list if new_obs_list else None

        # Make a map
        if form_params['show_map']:
            dso_list = [x.dso for x in context['dso_list']]
            if len(dso_list) == 0:
                context['map'] = None
            else:
                center_ra, center_dec, max_dist, fov = get_map_parameters(dso_list) #, mag=1.8)
                star_mag_limit = get_star_mag_limit(max_dist)
                map = plot_dso_list(
                    center_ra, 
                    center_dec,
                    dso_list,
                    fov=fov,
                    star_mag_limit = star_mag_limit,
                    reversed = False,
                    label_size='small',
                    symbol_size=60,
                    title = f"Imaging Sample"
                )
                context['map'] = map
        else:
            context['map'] = None
        context['table_id'] = 'dsos-on-list'
        return context
    
class DSORealTimeView(CookieMixin, DetailView):
    model = DSO
    template_name = 'real_time_popup.html'

    def get_context_data(self, **kwargs):
        context = super(DSORealTimeView, self).get_context_data(**kwargs)
        object = self.get_object()
        context['object_type'] = 'DSO'
        context['object'] = object
        context = get_real_time_conditions(object, self.request, context)
        return context
    
class DSOSearchView(View):

    def get(self, request):
        query = request.GET.get('query', None).lower()
        words, name = find_cat_id_in_string(query)
        target = search_dso_name(words, name)
        if target is not None:
            return redirect(target)
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
