import itertools
from re import L
from django.db.models import Count
from django.views.generic.base import TemplateView
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView, MultipleObjectMixin
from .models import Constellation, Catalog, ObjectType
from .utils import filter_dso_test
from ..dso.models import DSO, DSOAlias
from ..stars.models import BrightStar
from .helpers import get_objects_from_cookie

def try_int(x):
    try:
        return int(x)
    except:
        foo = "".join(itertools.takewhile(str.isdigit, x)) # "55-57" returns 55, pizza returns 0 
        if foo[0].isdigit:
            return int(foo)
        return 0

class ConstellationListView(ListView):
    """
    Generate list of constellations with metadata.
    """
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
    """
    Return a list of DSOs in the constellation.
    """
    model = Constellation 
    template_name = 'constellation_detail.html'

    def get_context_data(self, **kwargs):
        context = super(ConstellationDetailView, self).get_context_data(**kwargs)
        object = self.get_object()
        context['dso_list'] = DSO.objects.filter(constellation=object)
        context['table_id'] = 'dso_table'
        context['hide_constellation'] = True
        context['bright_stars'] = BrightStar.objects.filter(constellation__iexact=object.abbreviation.lower()).order_by('magnitude')
        
        # Add solar system objects that happen to be within the constellation from the session cookie
        context['planets'] = get_objects_from_cookie(self.request, 'planets', object.abbreviation)
        context['asteroids'] = get_objects_from_cookie(self.request, 'asteroids', object.abbreviation)
        context['comets'] = get_objects_from_cookie(self.request, 'comets', object.abbreviation)

        return context

class CatalogListView(ListView):
    model = Catalog
    template_name = 'catalog_list.html'

class CatalogDetailView(DetailView, MultipleObjectMixin):
    """
    Show all DSOs for a catalog.   Includes references where the catalog entry is 
    an alias, e.g., NGC 7654 will show up for M 52.
    Not a good idea for the NGC catalog.
    """
    model = Catalog
    template_name = 'catalog_detail.html'
    paginate_by = 40 

    def get_context_data(self, **kwargs):
        """
        OK - what I want here is to either:
            a) only show primary ID entries
            b) Anything that's an alias too
        """
        #context = super(CatalogDetailView, self).get_context_data(**kwargs)
        object = self.get_object()
        cat_list = Catalog.objects.all()
        primary_dsos = DSO.objects.filter(catalog=object)
        alias_dsos = DSO.objects.filter(aliases__catalog=object)

        if object.slug in ['messier', 'caldwell']: # Override pagination
            self.paginate_by = None

        filter_string = self.request.GET.get('filters', None)
        print("FILTER STRING: ", filter_string)
        filters = filter_string.split(',') if filter_string is not None else None

        # OK - somehow merge these two.
        all_objects = []
        for o in primary_dsos:
            if filters is not None and filter_dso_test(o, filters) is None:
                continue
            entry = {}
            entry['in_catalog'] = o.id_in_catalog
            entry['primary_catalog'] = None
            entry['dso'] = o
            all_objects.append(entry)
        for o in alias_dsos:
            if filters is not None and filter_dso_test(o, filters) is None:
                continue
            entry = {}
            entry['primary_catalog'] = o.shown_name
            entry['in_catalog'] = o.aliases.filter(catalog = object).first().id_in_catalog
            entry['dso'] = o
            all_objects.append(entry)
        
        try:
            all_objects_sort = sorted(all_objects, key=lambda d: try_int(d['in_catalog']))
        except:
            all_objects_sort = sorted(all_objects, key=lambda d: str(d['in_catalog']))
        
        context = super(CatalogDetailView, self).get_context_data(
            object_list=all_objects_sort, 
            **kwargs
        )
        
        context['catalog_list'] = cat_list
        context['table_id'] = f'cat_dso_{object.slug}'
        context['object_count'] = len(all_objects)
        return context

class ObjectTypeListView(ListView):
    """
    Generate metadata for a given Object Type.
    """
    model = ObjectType
    template_name = 'object_type_list.html'

    def get_context_data(self, **kwargs):
        context = super(ObjectTypeListView, self).get_context_data(**kwargs)
        object_list = ObjectType.objects.annotate(dso_count=Count('dso'))
        context['object_list'] = object_list
        return context

class ObjectTypeDetailView(DetailView):
    """
    Return the DSO list for a given Object Type.
    """
    model = ObjectType
    template_name = 'object_type_detail.html'

    def get_context_data(self, **kwargs):
        context = super(ObjectTypeDetailView, self).get_context_data(**kwargs)
        object = self.get_object()
        context['dso_list'] = DSO.objects.filter(object_type=object)
        context['hide_type'] = True
        context['table_id'] = 'dso_table_by_type'
        return context