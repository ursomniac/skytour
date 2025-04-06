import datetime as dt, pytz
import io
import time

from dateutil.parser import isoparse
from django.core.paginator import Paginator
from django.db.models import Count
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse, reverse_lazy
from django.utils.html import mark_safe
from django.views.generic.base import TemplateView, View
from django.views.generic.detail import DetailView
from django.views.generic.edit import UpdateView, FormView
from django.views.generic.list import ListView
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

from ..abstract.utils import get_real_time_conditions 
from ..abstract.vocabs import (
    IMAGE_CROPPING_OPTIONS, 
    IMAGE_ORIENTATION_CHOICES, 
    IMAGE_PROCESSING_STATUS_OPTIONS
)
from ..astro.time import get_datetime_from_strings
from ..session.pdf_pages.dso import do_dso_lists
from ..session.mixins import CookieMixin
from ..site_parameter.helpers import find_site_parameter
from ..tech.models import Telescope
from ..utils.timer import compile_times

from .atlas_utils import find_neighbors, assemble_neighbors
from .finder import plot_dso_list
from .forms import (
    DSOListCreateForm, 
    DSOListEditForm,
    DSOMetadataForm,
    DSOObservationEditForm,
)
from .geo import get_circle_center
from .helpers import get_star_mag_limit
from .mixins import AvailableDSOMixin
from .models import (
    DSO, DSOList, 
    AtlasPlate, 
    DSOImage, DSOLibraryImage, 
    DSOObservation, DSOObservingMode
)
from .observing import make_observing_date_grid, get_max_altitude
from .search import search_dso_name, find_cat_id_in_string
from .utils import (
    select_atlas_plate, 
    select_other_atlas_plates, 
    get_priority_label_of_observing_mode,
    get_priority_span_of_observing_mode,
    add_dso_to_dsolist,
    delete_dso_from_dsolist,
    construct_mode_form, 
    deconstruct_mode_form
)
from .utils_avail import assemble_gear_list, find_dsos_at_location_and_time
from .utils_checklist import (
    filter_dsos, 
    get_filter_params, 
    update_dso_filter_context
)
from .utils_dsolist import get_active_dsolist_objects, get_dso_list_map

class DSOListView(CookieMixin, ListView):
    model = DSO
    template_name = 'dso_list.html'
    context_object_name = 'dso_list'
    paginate_by = 100

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

    def get_context_data(self, **kwargs):
        context = super(DSOListView, self).get_context_data(**kwargs)
        context['create_form'] = DSOListCreateForm()
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
        context['use_mode'] = self.request.GET.get('use_mode', None)
        context['num_on_page'] = num_on_page
        p = Paginator(dso_list, num_on_page)
        this_page = p.page(page_no)
        context['page_obj'] = this_page
        context['dso_list'] = this_page.object_list # Just this page of objects.
        context['is_paginated'] = True
        context['table_id'] = 'dso_list'
        return context

class DSODetailView(CookieMixin, DetailView):
    model = DSO 
    template_name = 'dso_detail.html'

    def get_context_data(self, **kwargs):
        context = super(DSODetailView, self).get_context_data(**kwargs)
        times = [(time.perf_counter(), 'Start')]

        object = self.get_object()

        observing_mode = context['observing_mode']
        priority_label = get_priority_label_of_observing_mode(object, observing_mode)
        tmp_span = get_priority_span_of_observing_mode(object, observing_mode)
        priority_span = None if tmp_span is None else mark_safe(tmp_span)
        times.append((time.perf_counter(), 'Get priorities'))

        location = context['location']
        local_dt = isoparse(context['local_time_start'])
        context['local_dt_str'] = local_dt.strftime("%Ih%Mm %p")
        context['max_altitude'] = get_max_altitude(object, location=location)
        context['observing_date_grid'] = make_observing_date_grid(object)
        times.append((time.perf_counter(), 'Get alt/grid'))

        context['image_list'] = self.object.images.order_by('order_in_list')
        context['other_library_images'] = self.object.image_library.all() # [1:]
        context['library_slideshow'] = self.object.image_library.filter(use_in_carousel=1).order_by('order_in_list')
        context['map_slideshow'] = self.object.map_image_list
        context['finder_slideshow'] = self.object.finder_image_list
        context['other_metadata'] = self.object.other_metadata_text
        context['other_parameters'] = self.object.other_parameters
        times.append((time.perf_counter(), 'Get other metadata'))
        context['active_dsolists'] = self.object.dsolist_set.filter(active_observing_list=True)
        times.append((time.perf_counter(), 'Get DSO Lists'))
        context['mode_priority_label'] = priority_label
        context['mode_priority_span'] = priority_span
        context['times'] = compile_times(times)
        return context
    
class DSOListActiveView(TemplateView):
    template_name = 'dsolist_active.html'

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

    def get_context_data(self, **kwargs):
        context = super(DSOListActiveView, self).get_context_data(**kwargs)
        context['create_form'] = DSOListCreateForm()
        context['dso_lists'] = DSOList.objects.filter(active_observing_list=True)
        context['is_dsolist_page'] = True
        return context
    
class DSOListActiveDSOListView(CookieMixin, TemplateView):
    template_name = 'active_dsos_list.html'

    def get_context_data(self, **kwargs):
        context = super(DSOListActiveDSOListView, self).get_context_data(**kwargs)
        priority = int(self.request.GET.get('priority', 4))
        mode = self.request.GET.get('mode', context['observing_mode'])
        context['active_lists'] = DSOList.objects.filter(active_observing_list=True)
        context['priority'] = priority
        context['mode'] = mode
        context['dso_list'] = dso_list = get_active_dsolist_objects(mode, priority)
        context['num_dsos'] = len(context['dso_list'])
        context['map'] = get_dso_list_map(dso_list, priority, mode)
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
        context['hide_image'] = False
        return context
    
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
        show_thumbs = self.request.GET.get('show_thumbs', 'off') == 'on'
        context['show_thumbs'] = show_thumbs
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

        if context['is_now']:
            #print("Doing @Now")
            context['utdt'] = dt.datetime.now(dt.timezone.utc)
        else:
            #print("Doing @Cookie")
            if context['utdt'] is None or context['utdt'] == 'None':
                context['utdt'] = context['cookies']['user_pref']['utdt_start']

        orig_utdt = context['utdt']
        if type(orig_utdt) == str:
            format_utdt = orig_utdt
        else:
            format_utdt = orig_utdt.strftime("%Y-%m-%d %H:%M:%S")
            
        dso_list = DSO.objects.all()

        if debug:
            print("MIN DEC: ", min_dec)
            print("MAX_DEC: ", max_dec)
            print("# DSOS: ", dso_list.count())

        if min_dec is not None:
            dso_list = dso_list.filter(dec__gte=min_dec)
        if max_dec is not None:
            dso_list = dso_list.filter(dec__lte=max_dec)

        if debug:
            print("# DSOs 2: ", dso_list.count())

        up_dict, times = find_dsos_at_location_and_time (
            dsos = dso_list,                         # DSO List to start with - filtered by declination
            utdt = context['utdt'],                  # UTDT of now or the cookie
            offset_hours = context['ut_offset'],     # Offset the time as instructed
            imaged = context['imaged'],              # Only (don't) show objects with library images
            min_priority = context['min_priority'],  # Filter by priority
            location = location,                     # ObservingLocation object from the cookie
            min_alt = context['min_alt'],            # Minimum altitude
            max_alt = context['max_alt'],            # Maximum altitude
            mask = not no_mask,                      # Use location mask (for trees, buildings, etc.)
            gear = gear,                             # Filter by gear choices
            scheduled = is_scheduled,                # Only show objects on active DSOList objects
            debug=debug
        )
        dsos = up_dict['dsos']
        context['calc_utdt'] = up_dict['utdt']
        context['format_utdt'] = format_utdt
        context['local_time'] = up_dict['utdt'].astimezone(pytz.timezone(location.time_zone.pytz_name)).strftime("%A %b %-d, %Y %-I:%M %p %z")
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
        return context

class DSOManageExternalImageView(TemplateView):
    template_name = "manage_dso_image.html"
    model = DSO
    
    def post(self, request, *args, **kwargs):
        
        dso = get_object_or_404(DSO, pk=self.kwargs['pk'])
        if request.method == 'POST':
            # How many images are there to process (and then maybe add)?
            num_items = request.POST.get('num_images', "0")

            # Create an index for each image and the "new" image
            indexes = [str(x) for x in range(int(num_items))] + ['new']

            # Loop over the images
            for n in indexes:
                # Image - can be None if the file isn't changing!
                image_value = request.FILES.get(f"form-{n}-image", None)
                # Order in list
                order_value = int(request.POST.get(f"form-{n}-order", 0))
                # The PK if this is an UPDATE
                pk_value = request.POST.get(f"form-{n}-pk", None)
                # Delete
                delete_value = request.POST.get(f"form-{n}-delete", 'off') == 'on'

                img_object = None # default

                # Look up or Create a DSOImage instance
                if n != 'new': # This is an UPDATE (or DELETE) operation
                    if pk_value in [None ,'']:  # oops - we should have a PK
                        continue
                    # Look up the DSOImage instance
                    img_object = DSOImage.objects.filter(pk=int(pk_value)).first()
                    if not img_object: # oops - didn't find it - skip
                        continue
                    if delete_value: # Ah - this is a DELETE operation
                        img_object.delete()
                        continue
                else:  # This is a CREATE operation
                    img_object = DSOImage()
                    img_object.object_id = dso.pk # set the parent DSO

                # just in case that didn't go well and we didn't catch it
                if img_object is None: 
                    continue

                # Fill in the instance fields
                img_object.order_in_list = order_value
                if image_value is not None:
                    img_object.image = image_value
                
                # And now save it
                try:
                    img_object.save()
                except:
                    print("DSOImage Management - somwthing went wrong!")

        # Go back to the parent DSO Detail page
        return HttpResponseRedirect(reverse('dso-detail', kwargs={'pk': dso.pk}))

    def get_context_data(self, **kwargs):
        context = super(DSOManageExternalImageView, self).get_context_data(**kwargs)
        pk = self.kwargs['pk']
        dso = get_object_or_404(DSO, pk=pk)
        context['dso'] = dso
        context['images'] = dso.images.all()
        context['num_images'] = dso.images.count()
        context['extra'] = True
        return context
    
class DSOManageLibraryImagePanelView(TemplateView):
    model = DSO
    template_name = 'manage_dso_library_image_panel.html'

    def post(self, request, *args, **kwargs):
        def haz(x): # All the ways something isn't something
            return x not in [None, 'None', '']
        def nodash(x):
            return x.replace('-','').strip() == 0

        dso = get_object_or_404(DSO, pk=self.kwargs['pk'])
        panel = self.kwargs['panel']

        if request.method == "POST":

            # how many existing images are there to process?
            num_items = request.POST.get('num_images', "0")

            # These are the simpler fields on the form for each image
            keys = ['pk', 'order', 'utdate', 'uttime','exptime', 'telescope', 'proc', 'orientation', 'crop']
            # create an index for every object in the form - including "extra"
            indexes = [str(x) for x in range(int(num_items))] + ['extra']

            # loop through every object on the form
            for n in indexes:
                op = None
                vals = {} # Store all the .get() values in here
                for k in keys: # do the easy ones first
                    name = f"form-{n}-{k}"
                    vals[k] = request.POST.get(name, None)
                # deal with the other fields
                vals['image'] = request.FILES.get(f"form-{n}-image", None)
                vals['delete'] = request.POST.get(f"form-{n}-delete", 'off') == 'on'

                # Toss things if not complete
                if n != 'extra' and vals['pk'] is None: # I needed a PK!
                    print("No PK found for updating image.")
                    continue

                # Get the DSOLibrary object or create one
                if n != 'extra': # This is an UPDATE - get the instance
                    img_object = DSOLibraryImage.objects.filter(pk=int(vals['pk'])).first()
                    if img_object is None: # didn't find it
                        print("Could not find image to update")
                        continue
                    # If this is a DELETE operation - do it now
                    if vals['delete']:
                        print("DELETEING image")
                        img_object.delete()
                        continue
                    op = 'UPDATE'

                else: # This is an INSERT operation - create a new instance!
                    img_object = DSOLibraryImage()
                    img_object.object_id = dso.pk  # set the parent DSO
                    op = 'CREATE'
                
                # OK - fill in the fields!

                # which panel?
                if panel == 'slideshow':
                    img_object.use_as_map = 0
                    img_object.use_in_carousel = 1
                else:
                    img_object.use_as_map = 1
                    img_object.use_in_carousel = 0

                # image order
                if haz(vals['order']):
                    order_val = int(vals['order'])
                else:
                    order_val = 0
                img_object.order_in_list = order_val

                # the image itself
                # If an image isn't added, skip it
                # This is the case if you DIDN'T add a new image, and only edited the other ones
                if vals['image'] is not None: 
                    img_object.image = vals['image']
                else:
                    if op == 'CREATE': # No image to upload
                        continue

                # deal with date/time (two fields on the form map to a datetime object)
                new_dt = get_datetime_from_strings(vals['utdate'], vals['uttime'])
                if new_dt is not None:
                    img_object.ut_datetime = new_dt

                # deal with exposure time (float)
                if haz(vals['exptime']):
                    exptime = float(vals['exptime'])
                    img_object.exposure = exptime

                # deal with Telescope FK
                if haz(vals['telescope']): # and nodash(vals['telescope']):
                    tel_id = int(vals['telescope'])
                    img_object.telescope_id = tel_id

                # the others are all strings... so they're straightforward
                if haz(vals['proc']): # and nodash(vals['proc']):
                    img_object.image_processing_status = vals['proc']

                if haz(vals['orientation']): # and nodash(vals['orientation']):
                    img_object.image_orientation = vals['orientation']

                if haz(vals['crop']): # and nodash(vals['crop']):
                    img_object.image_cropping = vals['crop']

                print("READY TO SAFE: ", vals)
                img_object.save()

        
        # Go back to the parent DSO Detail page with the updated panel!
        return HttpResponseRedirect(reverse('dso-detail', kwargs={'pk': dso.pk}))

    def get_context_data(self, **kwargs):
        context = super(DSOManageLibraryImagePanelView, self).get_context_data(**kwargs)
        panel = self.kwargs['panel']
        pk = self.kwargs['pk']
        dso = get_object_or_404(DSO, pk=pk)

        image_list = dso.image_library.all()
        if panel == 'slideshow':
            image_list = image_list.filter(use_in_carousel=1).order_by('order_in_list')
        elif panel == 'landscape':
            image_list = image_list.filter(use_as_map=1).order_by('order_in_list')
        context['images'] = image_list
        context['num_images'] = image_list.count()
        context['extra'] = True
        context['telescopes'] = Telescope.objects.all()
        context['orientations'] = IMAGE_ORIENTATION_CHOICES
        context['croppings'] = IMAGE_CROPPING_OPTIONS
        context['procstats'] = IMAGE_PROCESSING_STATUS_OPTIONS
        return context
    
class DSOObservationEditView(UpdateView):
    model = DSOObservation
    form_class = DSOObservationEditForm
    template_name = 'dsoobservation_edit.html'
    
    def get_success_url(self):
        object = self.object
        return reverse_lazy('session-detail', kwargs={'pk': object.session.pk})
    
    def get_context_data(self, **kwargs):
        context = super(DSOObservationEditView, self).get_context_data(**kwargs)
        object = self.get_object()
        context['dso'] = object.object
        return context
    
class DSOListPDFView(View):
    
    def get_context_data(self, **kwargs):
        context = {}
        return context
    
    def get(self, request, *args, **kwargs):
        context = self.get_context_data()
        pk = kwargs.get('pk', None)
        if pk:
            dso_lists = DSOList.objects.filter(pk=pk)
            # Start file.
            buffer = io.BytesIO()
            p = canvas.Canvas('/tmp/foo.pdf', pagesize=letter)
            p = canvas.Canvas(buffer, pagesize=letter)
            p = do_dso_lists(p, context, dso_lists=dso_lists)     # DSO Lists       
            p.save()
            buffer.seek(0)
            response = HttpResponse(buffer, content_type='application/pdf')
            return response

class DSOObservingModeEditView(TemplateView):
    template_name = 'dsoobservingmode_edit.html'
    
    def get_context_data(self, **kwargs):
        context = super(DSOObservingModeEditView, self).get_context_data(**kwargs)
        pk = self.kwargs['pk']
        dso = context['dso'] = get_object_or_404(DSO, pk=pk)
        forms = {}
        for mode in 'NBSMI':
            mode_obj = dso.dsoobservingmode_set.filter(mode=mode).first()
            forms[mode] = construct_mode_form(mode, mode_obj, dso)
        context['mode_forms'] = forms
        return context
    
    def post(self, request, *args, **kwargs):
        dso = get_object_or_404(DSO, pk=self.kwargs['pk'])
        modes = dso.dsoobservingmode_set.all()
        if request.method == 'POST':
            data = request.POST
            for mode in 'NBSMI':
                item = modes.filter(mode=mode).first()
                vals, delete_flag = deconstruct_mode_form(data, mode)
                if delete_flag and item is not None:
                    item.delete()
                else:
                    if vals is not None:
                        if item is None:
                            item = DSOObservingMode() # INSERT
                            item.dso = dso
                            item.mode = mode

                        item.priority = vals['priority']
                        item.viable = vals['viable']
                        item.interesting = vals['interesting']
                        item.challenging = vals['challenging']
                        item.notes = vals['notes']
                        item.save()

        return HttpResponseRedirect(reverse('dso-detail', kwargs={'pk': dso.pk}))
