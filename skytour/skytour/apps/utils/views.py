#import itertools
from django.core.paginator import Paginator
from django.db.models import Count, IntegerField
from django.db.models.functions import Cast
from django.views.generic.base import TemplateView
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView, MultipleObjectMixin
from itertools import chain, takewhile
from operator import attrgetter
from .models import Constellation, Catalog, ObjectType
from .utils import filter_dso_test, get_filter_list
from ..dso.models import DSO, DSOLibraryImage
from ..solar_system.models import AsteroidLibraryImage, CometLibraryImage, PlanetLibraryImage
from ..stars.models import BrightStar
from .helpers import get_objects_from_cookie
from .models import ObjectType

def get_list_of_primary_library_images(qs):
    distinct_objects = qs.values('object').distinct()
    if qs.first() is None:
        return []
    model = qs.first().object.__class__ # this is the model
    pk_list = []
    for o in distinct_objects:
        pk_list.append(o['object'])
    object_list = model.objects.filter(pk__in=pk_list)
    image_list = []
    for obj in object_list:
        image_list.append(obj.image_library.order_by('order_in_list').first())
    
    return sorted(image_list, key = lambda img: img.ut_datetime, reverse = True)

def try_int(x):
    try:
        return int(x)
    except:
        foo = "".join(takewhile(str.isdigit, x)) # "55-57" returns 55, pizza returns 0 
        if foo[0].isdigit:
            return int(foo)
        return 0
    
def assemble_object_types():
    tt = ObjectType.objects.order_by('slug')
    l = []
    for t in tt:
        d = dict(label=t.short_name, slug=t.slug, spaces = range(15 - len(t.short_name)), type=1)
        l.append(d)
    l.append(dict(label='Asteroid', slug='asteroid', spaces = range(7), type=1))
    l.append(dict(label='Comet', slug='comet', spaces = range(10), type=1))
    l.append(dict(label='Planet', slug='planet', spaces = range(9), type=1))

    l.append(dict(label='Sol. System', slug='solar-system', spaces = range(4), type=2))
    l.append(dict(label='Galaxy', slug='galaxy', spaces=range(9), type=2))
    l.append(dict(label='Nebula', slug='nebula', spaces=range(9), type=2))
    l.append(dict(label='Cluster', slug='cluster', spaces=range(8), type=2))

    l.append(dict(label='All', slug='all', spaces=range(12), type=0))
    return l

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

        filters = get_filter_list(self.request)

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

GALAXY_TYPES = ['barred-spiral', 'dwarf-galaxy', 'galaxy--elliptical',
    'irregular-galaxy', 'galaxy--lenticular', 'seyfert-galaxy',
    'galaxy--spiral']
NEBULA_TYPES = ['cluster-nebulosity', 'dark-nebula', 'diffuse-nebula',
    'nebula--emission', 'interstellar-matter', 'planetary-nebula',
    'reflection-nebula', 'supernova-remnant']
CLUSTER_TYPES = ['asterism', 'globular-cluster', 'open-cluster',
    'stellar-association']

class LibraryImageView(TemplateView):
    template_name = 'library_image_list.html'
    paginate_by = 15

    def get_context_data(self, **kwargs):
        context = super(LibraryImageView, self).get_context_data(**kwargs)
        object_type = kwargs.get('object_type', None)
        object_type = None if object_type == 'all' else object_type
        object_count = 0

        asteroid_image_list = []
        comet_image_list = []
        planet_image_list = []
        dso_image_list = []

        sso_object_types = ['asteroid', 'comet', 'planet', 'solar-system']
        # Asteroid
        if object_type in ['asteroid', 'solar-system', None]:
            asteroid_images = AsteroidLibraryImage.objects.order_by('-ut_datetime')
            asteroid_image_list = get_list_of_primary_library_images(asteroid_images)
            object_count += asteroid_images.values('object').distinct().count()
        # Comet
        if object_type in ['comet', 'solar-system', None]:
            comet_images = CometLibraryImage.objects.order_by('-ut_datetime')
            comet_image_list = get_list_of_primary_library_images(comet_images)
            object_count += comet_images.values('object').distinct().count()

        # Planet
        if object_type in ['planet', 'solar-system', None]:
            planet_images = PlanetLibraryImage.objects.order_by('-ut_datetime')
            planet_image_list = get_list_of_primary_library_images(planet_images)
            object_count += planet_images.values('object').distinct().count()
        # DSOs
        if object_type not in sso_object_types or object_type is None:
            if object_type is None:
                dso_images = DSOLibraryImage.objects.order_by('-ut_datetime', 'order_in_list')
            elif object_type == 'galaxy':
                dso_images = DSOLibraryImage.objects.filter(object__object_type__slug__in=GALAXY_TYPES)
            elif object_type == 'nebula':
                dso_images = DSOLibraryImage.objects.filter(object__object_type__slug__in=NEBULA_TYPES)
            elif object_type == 'cluster':
                dso_images = DSOLibraryImage.objects.filter(object__object_type__slug__in=CLUSTER_TYPES)
            else:
                dso_images = DSOLibraryImage.objects.filter(object__object_type__slug=object_type).order_by('-ut_datetime')
            dso_image_list = get_list_of_primary_library_images(dso_images)
            object_count += dso_images.values('object').distinct().count()

        #all_image_list = list(chain(dso_image_list, asteroid_image_list, comet_image_list, planet_image_list))
        all_image_list = sorted(
            chain(
                dso_image_list, 
                planet_image_list, 
                comet_image_list, 
                asteroid_image_list
            ),
            key = lambda instance: instance.ut_datetime,
            reverse = True
        )
        # Pagination
        context['page_error'] = None
        page_no = self.request.GET.get('page', 1)
        num_on_page = self.request.GET.get('page_size', self.paginate_by)
        p = Paginator(all_image_list, num_on_page)
        try:
            this_page = p.page(page_no)
        except:
            this_page = p.page(1)
            context['page_error'] = "Requested page not valid.  Resetting to the first page."
        context['page_obj'] = this_page
        context['image_list'] = this_page.object_list # Just this page of objects.
        context['is_paginated'] = True

        context['image_list_count'] = len(all_image_list)
        context['object_count'] = object_count
        return context
    
class LibraryCatalogView(TemplateView):
    template_name = 'library_catalog_list.html'

    def get_context_data(self, **kwargs):
        context = super(LibraryCatalogView, self).get_context_data(**kwargs)
        catalog_slug = self.request.GET.get('catalog_slug', 'messier') # or 'caldwell'
        all = self.request.GET.get('scope') == 'all'

        # This only works when the catalog request is the primary ID for the DSO
        # So, only Messier and Caldwell.
        # TODO: Have it check aliases too. 
        raw_dso_list = DSO.objects.filter(catalog__slug=catalog_slug).exclude(priority='None')
        raw_dso_list = raw_dso_list.annotate(cid=Cast('id_in_catalog', IntegerField())).order_by('cid', 'id_in_catalog')
        # deal with C14 = NGC 869 and NGC 884 - both are C 14 but they have two separate
        #   records in the DSO table because the primary IDs have to be unique.
        if catalog_slug == 'caldwell': 
            extra = DSO.objects.filter(catalog__slug='ngc', id_in_catalog__in=['869', '884'])
            extra = extra.annotate(cid=Cast('id_in_catalog', IntegerField())).order_by('cid', 'id_in_catalog')
            for e in extra:
                e.cid = 14
            dso_list = sorted(chain(raw_dso_list, extra), key = attrgetter('cid'))
        else:
            dso_list = raw_dso_list
                                                      
        imaged_dso_list =  [x  for x in dso_list if x.num_library_images > 0]
        context['object_list'] = dso_list if all else imaged_dso_list
        context['object_count'] = len(dso_list)
        context['image_list_count'] = len(imaged_dso_list)
        context['image_percent'] = 100. * len(imaged_dso_list) / len(dso_list)
        context['catalog'] = 'Messier' if catalog_slug == 'messier' else 'Caldwell'
        return context