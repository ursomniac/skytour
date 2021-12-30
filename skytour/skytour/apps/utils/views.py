from django.db.models import Count
from django.views.generic.base import TemplateView
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from .models import Constellation, Catalog, ObjectType
from ..dso.models import DSO, DSOAlias

def try_int(x):
    try:
        return int(x)
    except:
        return x

class ConstellationListView(ListView):
    model = Constellation
    template_name = 'constellation_list.html'

    def get_context_data(self, **kwargs):
        context = super(ConstellationListView, self).get_context_data(**kwargs)
        object_list = Constellation.objects.annotate(dso_count=Count('dso'))
        context['object_list'] = object_list
        context['include_zero'] = False
        context['table_id'] = 'constellation_list'
        return context

class ConstellationDetailView(DetailView):
    model = Constellation 
    template_name = 'constellation_detail.html'

    def get_context_data(self, **kwargs):
        context = super(ConstellationDetailView, self).get_context_data(**kwargs)
        object = self.get_object()
        context['dso_list'] = DSO.objects.filter(constellation=object)
        context['table_id'] = 'dso_table'
        context['hide_constellation'] = True
        return context

class CatalogDetailView(DetailView):
    model = Catalog
    template_name = 'catalog_detail.html'

    def get_context_data(self, **kwargs):
        """
        OK - what I want here is to either:
            a) only show primary ID entries
            b) Anything that's an alias too
        """
        context = super(CatalogDetailView, self).get_context_data(**kwargs)
        object = self.get_object()
        primary_dsos = DSO.objects.filter(catalog=object)
        alias_dsos = DSO.objects.filter(aliases__catalog=object)

        # OK - somehow merge these two.
        all_objects = []
        for o in primary_dsos:
            entry = {}
            entry['in_catalog'] = o.id_in_catalog
            entry['primary_catalog'] = None
            entry['dso'] = o
            all_objects.append(entry)
        for o in alias_dsos:
            entry = {}
            entry['primary_catalog'] = o.shown_name
            entry['in_catalog'] = o.aliases.filter(catalog = object).first().id_in_catalog
            entry['dso'] = o
            all_objects.append(entry)
        all_objects_sort = sorted(all_objects, key=lambda d: try_int(d['in_catalog']))
        context['catalog_objects'] = all_objects_sort
        return context

class ObjectTypeListView(ListView):
    model = ObjectType
    template_name = 'object_type_list.html'

    def get_context_data(self, **kwargs):
        context = super(ObjectTypeListView, self).get_context_data(**kwargs)
        object_list = ObjectType.objects.annotate(dso_count=Count('dso'))
        context['object_list'] = object_list
        return context

class ObjectTypeDetailView(DetailView):
    model = ObjectType
    template_name = 'object_type_detail.html'

    def get_context_data(self, **kwargs):
        context = super(ObjectTypeDetailView, self).get_context_data(**kwargs)
        object = self.get_object()
        context['dso_list'] = DSO.objects.filter(object_type=object)
        context['hide_type'] = True
        context['table_id'] = 'dso_table_by_type'
        return context