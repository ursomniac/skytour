from collections import Counter
from dateutil.parser import isoparse
from django.db.models import Q, Count
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.views.generic.base import TemplateView
from django.views.generic.detail import DetailView
from django.views.generic.edit import FormView
from django.views.generic.list import ListView
from reportlab.pdfgen import canvas
from ..astro.culmination import get_opposition_date_at_time
from ..session.mixins import CookieMixin
from ..utils.timer import compile_times
from .atlas_utils import find_neighbors, assemble_neighbors
from .finder import create_dso_finder_chart, plot_dso_list
from .forms import DSOFilterForm, DSOAddForm
from .helpers import get_map_parameters, get_star_mag_limit
from .models import DSO, DSOList, AtlasPlate, DSOObservation, DSOImagingChecklist
from .utils import select_atlas_plate
from .utils_checklist import checklist_form, checklist_params, create_new_observing_list
from .vocabs import PRIORITY_CHOICES

class DSOListView(ListView):
    model = DSO
    template_name = 'dso_list.html'
    context_object_name = 'dso_list'
    paginate_by = 100

    def get_context_data(self, **kwargs):
        context = super(DSOListView, self).get_context_data(**kwargs)
        context['table_id'] = 'dso_list'
        return context

class DSODetailView(CookieMixin, DetailView):
    model = DSO 
    template_name = 'dso_detail.html'

    def get_context_data(self, **kwargs):
        context = super(DSODetailView, self).get_context_data(**kwargs)
        now = self.request.GET.get('now', False)
        planets_dict = context['cookies']['planets'] if now else None
        asteroid_list = context['cookies']['asteroids'] if now else None
        comet_list = context['cookies']['comets'] if now else None
        utdt = context['utdt_start']
        local_dt = isoparse(context['local_time_start'])
        #print("local dt type: ", type(local_dt), local_dt)
        hours = local_dt.hour + local_dt.minute/60. + local_dt.second/3600.
        context['local_dt_str'] = local_dt.strftime("%Ih%Mm %p")
        culm_at_time = get_opposition_date_at_time(self.object.ra, hours)
        context['culmination_at_time'] = culm_at_time

        #finder_chart, times1 = create_dso_finder_chart(
        #    self.object, 
        #    utdt = utdt, 
        #    planets_dict = planets_dict, 
        #    asteroid_list = asteroid_list,
        #    comet_list = comet_list,
        #    now = now
        #)
        #close_up_finder, times2 = create_dso_finder_chart(
        #    self.object,
        #    utdt = context['utdt_start'],
        #    fov = 2.,
        #    mag_limit = 11.,
        #    show_other_dsos = False,
        #    now = now,
        #    planets_dict=planets_dict,
        #    asteroid_list=asteroid_list,
        #    comet_list=comet_list
        #)
        #context['close_up_finder'] = close_up_finder
        #context['live_finder_chart'] = finder_chart
        # TODO: Add rise set times if cookie is set.
        #times = times1 + times2
        #context['times'] = compile_times(times)

        # 2023-07-24 images
        #my_images = self.object.images.filter(own_image=1).order_by('order_in_list')
        #if len(my_images) > 0:
        #    context['my_image'] = my_images.first()
        #    context['has_image'] = True
        #else:
        #    context['my_image'] = None
        #    context['has_image'] = False

        # 2023-08-19 images
        context['image_list'] = self.object.images.order_by('order_in_list')
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
        
        # Make a map
        dso_list = self.object.dso.all()
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
        print ("FORM PARAMS: ", form_params)
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
    