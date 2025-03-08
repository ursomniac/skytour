import datetime as dt, pytz
from dateutil.parser import isoparse

from django.db.models import Q, Count
from django.core.paginator import Paginator
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.html import mark_safe
from django.views.generic.base import TemplateView, View
from django.views.generic.detail import DetailView
from django.views.generic.edit import FormView, UpdateView
from django.views.generic.list import ListView

from ..abstract.utils import get_real_time_conditions
from ..session.mixins import CookieMixin
from ..site_parameter.helpers import find_site_parameter
from ..utils.timer import compile_times

from .atlas_utils import find_neighbors, assemble_neighbors
from .finder import plot_dso_list
from .forms import (
    DSOFilterForm, 
    DSOAddForm, 
    DSOListCreateForm, 
    DSOListEditForm,
    DSOMetadataForm
)
from .geo import get_circle_center
from .helpers import get_map_parameters, get_star_mag_limit
from .mixins import AvailableDSOMixin
from .models import DSO, DSOList, AtlasPlate
from .observing import make_observing_date_grid, get_max_altitude
from .search import search_dso_name, find_cat_id_in_string
from .utils import (
    select_atlas_plate, 
    select_other_atlas_plates, 
    get_priority_label_of_observing_mode,
    get_priority_span_of_observing_mode,
    add_dso_to_dsolist,
    delete_dso_from_dsolist
)
from .utils_avail import assemble_gear_list, find_dsos_at_location_and_time
from .utils_checklist import (
    checklist_form, 
    checklist_params, 
    create_new_observing_list,
    filter_dsos, 
    get_filter_params, 
    update_dso_filter_context
)

# TODO V2: Fix filtering for priority!
# TODO V2: Add mode considerations!
class DSOListView(CookieMixin, ListView):
    model = DSO
    template_name = 'dso_list.html'
    context_object_name = 'dso_list'
    paginate_by = 100

    def get_context_data(self, **kwargs):
        context = super(DSOListView, self).get_context_data(**kwargs)
        params = get_filter_params(self.request)
        context = update_dso_filter_context(context, params)
        dso_list = filter_dsos(params, DSO.objects.all())
        context['total_count'] = len(dso_list)
        # Deal with Declination
        if 'dec_range' in context.keys():
            try:
                dlo, dhi = context['dec_range']
                context['dec_low'] = dlo
                context['dec_high'] = dhi
            except:
                pass
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
        print('context: ', context.keys())
        print('DEC: ', context['dec_low'], context['dec_high'])
        print('RANGE: ', context['dec_range'])
        return context

class DSODetailView(CookieMixin, DetailView):
    model = DSO 
    template_name = 'dso_detail.html'

    def get_context_data(self, **kwargs):
        context = super(DSODetailView, self).get_context_data(**kwargs)
        object = self.get_object()

        observing_mode = context['observing_mode']
        priority_label = get_priority_label_of_observing_mode(object, observing_mode)
        tmp_span = get_priority_span_of_observing_mode(object, observing_mode)
        priority_span = None if tmp_span is None else mark_safe(tmp_span)

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
        context['active_dsolists'] = self.object.dsolist_set.filter(active_observing_list=True)
        context['mode_priority_label'] = priority_label
        context['mode_priority_span'] = priority_span
        return context
    
class DSOListActiveView (TemplateView):
    template_name = 'dsolist_active.html'

    def get_context_data(self, **kwargs):
        context = super(DSOListActiveView, self).get_context_data(**kwargs)
        context['dso_lists'] = DSOList.objects.filter(active_observing_list=True)
        context['is_dsolist_page'] = True
        return context

class DSOListListView(CookieMixin, ListView):
    model = DSOList
    template_name = 'dsolist_list.html'

    def get_context_data(self, **kwargs):
        context = super(DSOListListView, self).get_context_data(**kwargs)
        context['create_form'] = DSOListCreateForm()
        return context
    
    def post(self, request, *args, **kwargs):
        form = DSOListCreateForm(request.POST)
        if form.is_valid():
            d = form.cleaned_data
            obj = DSOList()
            obj.name = d['name']
            obj.description = d['description']
            obj.active_observing_list = d['active_observing_list']
            obj.save()
        return self.get(request, *args, **kwargs)

class DSOListDetailView(CookieMixin, DetailView):
    model = DSOList
    template_name = 'dsolist_detail.html'

    def post(self, request, *args, **kwargs):
        form = DSOListEditForm(request.POST)
        if form.is_valid():
            d = form.cleaned_data
            obj = self.get_object()
            print("OBJ: ", obj)

            if d['delete_checkbox']:
                obj.delete()
                return redirect('dsolist-list')
            else:
                obj.name = d['name']
                obj.description = d['description']
                obj.active_observing_list = d['active_observing_list']
                obj.save()
            return self.get(request, *args, **kwargs)

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
        context['is_dsolist_page'] = True
        # Deal with Edit form
        initial = {'name': object.name, 'description': object.description, 'active_observing_list': object.active_observing_list}
        context['edit_form'] = DSOListEditForm(initial=initial)
        context['object'] = object
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
        neighbors = find_neighbors(obj.center_ra, obj.center_dec, limit=30.)
        context['assembled_neighbors'] = assemble_neighbors(neighbors)
        return context

class DSOObservationLogView(CookieMixin, ListView):
    model = DSO
    template_name = 'dsoobservation_list.html'
    paginate_by = 50

    def get_context_data(self, **kwargs):
        context = super(DSOObservationLogView, self).get_context_data(**kwargs)
        context['dso_list'] = DSO.objects.annotate(nobs=Count('observations')).filter(nobs__gt=0).order_by('-nobs')
        context['dso_table'] = 'dsos-observed'
        context['total_count'] = context['dso_list'].count()
        
        # Pagination
        page_no = self.request.GET.get('page', 1)
        num_on_page = self.request.GET.get('page_size', self.paginate_by)
        context['num_on_page'] = num_on_page
        p = Paginator(context['dso_list'], num_on_page)
        this_page = p.page(page_no)
        context['page_obj'] = this_page
        context['dso_list'] = this_page.object_list # Just this page of objects.
        context['is_paginated'] = True
        return context
    
class DSOChecklistView(CookieMixin, ListView):
    # TODO V2: Deal with priority filter!
    # FIX: 
    #   1. Add mode to form (default = current mode)
    #   2. add that to filtering
    model = DSO
    template_name = 'imaging_checklist.html'
    paginate_by = 100

    def get_context_data(self, **kwargs):
        context = super(DSOChecklistView, self).get_context_data(**kwargs)
        # Deal with form
        form_params = checklist_params(self.request)
        # print ("FORM PARAMS: ", form_params)
        all_dsos = DSO.objects.all()
        
        #context['seen'] = 'checked' if form_params['seen'] else ''
        context['priority'] = form_params['priority']
        context['dso_type'] = form_params['dso_type'] if form_params['dso_type'] != 'all' else ''
        context['constellation'] = form_params['constellation'] if form_params['constellation'] else ''
        context['subset'] = form_params['subset'] if form_params['subset'] else 'all'
        context['exclude_issues'] = form_params['exclude_issues']
        context['dso_list'] = checklist_form(form_params, all_dsos)
        context['list_count'] = context['dso_list'].count()
        context['show_map'] = form_params['show_map']
        use_mode = form_params['use_mode']
        context['use_mode'] = use_mode if use_mode is not None else context['observing_mode']
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
            dso_list = context['dso_list']
            context['map'] = None
        context['table_id'] = 'dsos-on-list'

        # Pagination
        page_no = self.request.GET.get('page', 1)
        num_on_page = self.request.GET.get('page_size', self.paginate_by)
        context['num_on_page'] = num_on_page
        p = Paginator(context['dso_list'], num_on_page)
        this_page = p.page(page_no)
        context['page_obj'] = this_page
        context['dso_list'] = this_page.object_list # Just this page of objects.
        context['is_paginated'] = True
        return context
    
class DSORealTimeView(CookieMixin, DetailView):
    """
    Get Observing Metadata in RealTime
    """
    model = DSO
    template_name = 'real_time_popup.html'

    def get_context_data(self, **kwargs):
        context = super(DSORealTimeView, self).get_context_data(**kwargs)
        object = self.get_object()
        context['object_type'] = 'DSO'
        context['object'] = object
        context = get_real_time_conditions(object, self.request, context)
        return context
        
class DSOAdjustDSOListView(TemplateView):
    template_name = 'dsolist_adjust_popup.html'

    def get_context_data(self, **kwargs):
        context = super(DSOAdjustDSOListView, self).get_context_data(**kwargs)
        dso_pk = self.kwargs['pk']
        context['op'] = op = self.kwargs['op']
        context['result'] = None 

        # Get relevant objects
        context['dso'] = dso = DSO.objects.filter(pk=dso_pk).first()
        dso_lists = DSOList.objects.filter(active_observing_list=1).order_by('-pk')
        if op == 'delete':
            dso_lists = dso_lists.filter(dso=dso)
        context['dso_lists'] = dso_lists

        # Handle form
        dsolist_pk = self.request.GET.get('dso_list', None)
        dsolist = DSOList.objects.filter(pk=dsolist_pk).first()

        if dsolist_pk is None:
            context['result'] = None
        elif op == 'add':
            context['result'] = add_dso_to_dsolist(dso, dsolist)
        elif op == 'delete':
            context['result'] = delete_dso_from_dsolist(dso, dsolist)

        return context
    
class DSOSearchView(View):
    """
    Look up a DSO from name, alias, or DSOInField
    """
    def get(self, request):
        query = request.GET.get('query', None).lower()
        words, name = find_cat_id_in_string(query)
        target = search_dso_name(words, name)
        if target is not None:
            return redirect(target)
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

class AvailableDSOObjectsView(CookieMixin, AvailableDSOMixin, TemplateView):
    """
    This handles the @Now and @Cookie functions - the only difference is
        using the cookie has a GET value.  Both presume the ObservingLocation
        object in the cookie is the "right" value.
    """
    template_name = 'home_objects.html'

    def get_context_data(self, **kwargs):
        context = super(AvailableDSOObjectsView, self).get_context_data(**kwargs)
        debug = self.request.GET.get('debug', False)
        no_mask = self.request.GET.get('no_mask', 'off') == 'on'
        context['no_mask'] = no_mask
        is_scheduled  = self.request.GET.get('scheduled', 'off') == 'on'
        context['scheduled'] = is_scheduled
        use_cookie = self.request.GET.get('cookie', False)
        gear = assemble_gear_list(self.request)        
        location = context['cookies']['user_pref']['location']

        min_dec, max_dec = location.declination_range
        if context['min_dec'] is None:
            context['min_dec'] = min_dec
        if context['max_dec'] is None:
            context['max_dec'] = max_dec
        if context['min_alt'] is None:
            context['min_alt'] = find_site_parameter('minimum-object-altitude', default=10., param_type='float')
        if context['max_alt'] is None:
            context['max_alt'] = find_site_parameter('slew-limit', default=90., param_type='float')
        context['min_dec_string'] = f"{context['min_dec']:.1f}"
        context['max_dec_string'] = f"{context['max_dec']:.1f}"

        if use_cookie:
            if context['utdt'] is None or context['utdt'] == 'None':
                context['utdt'] = context['cookies']['user_pref']['utdt_start']
        else: 
            context['utdt'] = dt.datetime.now(dt.timezone.utc)

        orig_utdt = context['utdt']
        if type(orig_utdt) == str:
            format_utdt = orig_utdt
        else:
            format_utdt = orig_utdt.strftime("%Y-%m-%d %H:%M:%S")

        dso_list = DSO.objects.all()
        if min_dec is not None:
            dso_list = dso_list.filter(dec__gte=min_dec)
        if max_dec is not None:
            dso_list = dso_list.filter(dec__lte=max_dec)

        up_dict, times = find_dsos_at_location_and_time (
            dsos = dso_list,                         # DSO List to start with - filtered by declination
            utdt = context['utdt'],                  # UTDT of now or the cookie
            offset_hours = context['ut_offset'],     # Offset the time as instructed
            imaged = context['imaged'],              # Only (don't) show objects with library images
            min_priority = context['min_priority'],  # Filter by priority
            location = location,                     # ObservingLocation object from the cookie
            min_alt = context['min_alt'],            # Minimum altitude
            max_alt = context['max_alt'],            # Maximum altitude
            min_dec = context['min_dec'],            # Absolute range of declination
            max_dec = context['max_dec'],            # Absolute range of declination
            mask = not no_mask,                      # Use location mask (for trees, buildings, etc.)
            gear = gear,                             # Filter by gear choices
            scheduled = is_scheduled                 # Only show objects on active DSOList objects
        )
        dsos = up_dict['dsos']
        context['calc_utdt'] = up_dict['utdt']
        context['format_utdt'] = format_utdt
        context['local_time'] = up_dict['utdt'].astimezone(pytz.timezone(location.time_zone.name)).strftime("%A %b %-d, %Y %-I:%M %p %z")
        context['dso_list'] = dsos
        context['dso_count'] = dsos.count()
        context['table_id'] = 'available_table'
        context['location'] = up_dict['location']
        context['times'] = compile_times(times)

        # Set gear in form
        for g in 'NBSMI':
            context[f'gear{g}'] = g if gear and g in gear else None

        return context

class DSOEditMetadataView(UpdateView):
    model = DSO
    form_class = DSOMetadataForm
    template_name = 'edit_dso_metadata.html'

    def get_context_data(self, **kwargs):
        context = super(DSOEditMetadataView, self).get_context_data(**kwargs)
        context['dso'] = self.get_object()
        print("GOT HERE! DSO: ", context['dso'])
        return context