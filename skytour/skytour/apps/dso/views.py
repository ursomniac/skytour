from collections import Counter
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.views.generic.base import TemplateView
from django.views.generic.detail import DetailView
from django.views.generic.edit import FormView
from django.views.generic.list import ListView
from ..session.mixins import CookieMixin
from ..utils.timer import compile_times
from .finder import create_dso_finder_chart, plot_dso_list
from .forms import DSOFilterForm, DSOAddForm
from .models import DSO, DSOList
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
        planets_dict = context['cookies']['planets']
        asteroid_list = context['cookies']['asteroids']
        finder_chart, times = create_dso_finder_chart(
            self.object, 
            utdt = context['utdt_start'], 
            planets_dict = planets_dict, 
            asteroid_list = asteroid_list
        )
        context['live_finder_chart'] = finder_chart
        context['times'] = compile_times(times)
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

class DSOCatalogView(ListView):
    """
    This creates a PDF catalog (printable).
    """
    model = DSO

class DSOListListView(CookieMixin, ListView):
    model = DSOList
    template_name = 'dsolist_list.html'

class DSOListDetailView(CookieMixin, DetailView):
    model = DSOList
    template_name = 'dsolist_detail.html'

    def _map_params(self):
        min_ra, max_ra = self.object.ra_range
        min_dec, max_dec = self.object.dec_range
        center_ra = 0.5*(min_ra + max_ra)
        if center_ra < min_ra or center_ra > max_ra:
            center_ra += 12.
            center_ra %= 24.
        center_dec = 0.5*(min_dec + max_dec)
        ra_deg = 15. * (max_ra - min_ra)
        if ra_deg < 0:
            ra_deg = 360-ra_deg
        dec_deg = max_dec - min_dec
        fov = dec_deg if dec_deg > ra_deg else ra_deg
        fov *= 1.25
        return center_ra, center_dec, fov

    def get_context_data(self, **kwargs):
        context = super(DSOListDetailView, self).get_context_data(**kwargs)
        # Make a map
        center_ra, center_dec, fov = self._map_params()
        dso_list = self.object.dso.all()
        map = plot_dso_list(
            center_ra, 
            center_dec,
            dso_list,
            fov=fov,
            star_mag_limit = 7,
            reversed = False,
            label_size='small',
            symbol_size=60,
            title = f"DSO List: {self.object.name}"
        )
        context['map'] = map
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

        #return render(request, self.template_name, {})
        return HttpResponseRedirect(reverse('dsolist-detail', args=[dso_list.pk]))

