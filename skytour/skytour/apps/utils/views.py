from django.core.paginator import Paginator
from django.db.models import Count, IntegerField
from django.db.models.functions import Cast
from django.views.generic.base import TemplateView
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView, MultipleObjectMixin
from itertools import chain
from operator import attrgetter
from .assemble import assemble_catalog
from .helpers import get_objects_from_cookie
from .models import Constellation, Catalog, ObjectType
from .utils import filter_catalog, get_active_variable_stars, get_annals_variable_stars, get_variable_stars
from ..dso.models import DSO, DSOLibraryImage
from ..solar_system.models import AsteroidLibraryImage, CometLibraryImage, PlanetLibraryImage
from ..stars.models import BrightStar
from ..stars.utils import order_bright_stars

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

def assemble_constellation_list():
    return list(Constellation.objects.values_list('abbreviation', flat=True))

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
        context['table_id'] = 'constellation_dso_table'
        context['hide_constellation'] = True
        # BUG: This only gets stars with Bayer/Flamsteed numbers!
        #   The model ingest data doesn't have constellations for the others
        # TODO: Add a field to BrightStar and add in the constellations!
        stars = BrightStar.objects.filter(constellation__abbreviation=object.abbreviation.upper()).order_by('magnitude')
        context['bright_stars'] = order_bright_stars(stars)
        ###
        ### Variable Stars:
        # Need to get everything that has annals OR active
        context['variable_stars'] = get_variable_stars(object)
        #context['active_variable_stars'] = get_active_variable_stars(object)
        #context['annals_variable_stars'] = get_annals_variable_stars(object)
        # TODO: Add 'other_stars', 'double_stars',  to the star list
        # 
        
        # Add solar system objects that happen to be within the constellation from the session cookie
        context['planets'] = get_objects_from_cookie(self.request, 'planets', object.abbreviation)
        context['asteroids'] = get_objects_from_cookie(self.request, 'asteroids', object.abbreviation)
        context['comets'] = get_objects_from_cookie(self.request, 'comets', object.abbreviation)
        return context
    
class ConstellationWikiPopup(DetailView):
    model = Constellation
    template_name = 'wiki_content.html'

    def get_context_data(self, **kwargs):
        context = super(ConstellationWikiPopup, self).get_context_data(**kwargs)
        constellation = self.get_object()
        text = constellation.wiki.summary
        html_output = "".join(f"<p>{line.strip()}</p>\n" for line in text.strip().splitlines())
        context['text'] = html_output
        return context
    

class CatalogListView(ListView):
    model = Catalog
    template_name = 'catalog_list.html'

    def get_context_data(self, **kwargs):
        context = super(CatalogListView, self).get_context_data(**kwargs)
        context['table_id'] = 'catalog-list-table'
        return context

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
        object = self.get_object()
        cookie = self.request.session.get('user_preferences', None)
        cat_list = Catalog.objects.order_by('slug')
        #primary_dsos = DSO.objects.filter(catalog=object)
        #alias_dsos = DSO.objects.filter(aliases__catalog=object)
        #field_dsos = DSOInField.objects.filter(catalog=object) if object.slug != 'hickson' else []
        
        # deal with pagination and filtering
        params = self.request.GET.copy()
        params.pop('page', None)
        querystring = params.urlencode()
        hidden = ''
        p_obs = params.get('observed', None)
        if p_obs:
            hidden += f'<input type="hidden" name="observed" value="{p_obs}"/>'
        p_img = params.get('imaged', None)
        if p_img:
            hidden += f'<input type="hidden" name="imaged" value="{p_img}"/>'
        p_con = params.get('constellation', None)
        if p_con:
            hidden += f'<input type="hidden" name="constellation" value="{p_con}"/>'

        if object.slug in ['messier', 'caldwell', 'abell', 'hickson']: # Override pagination
            self.paginate_by = None

        all_objects_sort = assemble_catalog(object.slug, in_field=True)
        dso_list = filter_catalog(self.request, all_objects_sort, cookie)
        #all_objects_sort = new_objects_sort(object, primary_dsos, alias_dsos, field_dsos)
        #dso_list = filter_catalog(self.request, all_objects_sort, cookie)
        context = super(CatalogDetailView, self).get_context_data(
            object_list=dso_list,
            **kwargs
        )
        context['hidden'] = hidden
        context['filtered_object_list'] = dso_list
        context['catalog_list'] = cat_list
        context['table_id'] = f'cat_dso_{object.slug}'
        context['all_object_count'] = len(all_objects_sort)
        context['object_count'] = len(dso_list)

        context['constellation'] = self.request.GET.get('constellation', None)
        context['observed'] = self.request.GET.get('observed', None)
        context['imaged'] = self.request.GET.get('imaged', None)
        context['available'] = self.request.GET.get('available', None)
        context['qs'] = querystring
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

GALAXY_TYPES = ['galaxy--barred-spiral', 'galaxy--cluster', 'galaxy--dwarf', 'galaxy--elliptical',
    'galaxy--intermediate', 'galaxy--irregular', 'galaxy--lenticular', 
    'galaxy--spiral', 'galaxy--unclassified', 'galaxy--compact-group']
NEBULA_TYPES = ['cluster-nebulosity', 'dark-nebula', 'diffuse-nebula',
    'nebula--emission', 'interstellar-matter', 'planetary-nebula',
    'reflection-nebula', 'supernova-remnant']
CLUSTER_TYPES = ['asterism', 'globular-cluster', 'open-cluster',
    'stellar-association']

class LibraryImageView(TemplateView):
    template_name = 'library_image_list.html'
    paginate_by = 24

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
        context['constellation_list'] = assemble_constellation_list()
        return context
    
class LibraryCatalogView(TemplateView):
    template_name = 'library_catalog_list.html'

    def get_context_data(self, **kwargs):
        context = super(LibraryCatalogView, self).get_context_data(**kwargs)
        catalog_slug = self.request.GET.get('catalog_slug', 'messier') 
        all = self.request.GET.get('scope') == 'all'
        catalog = Catalog.objects.filter(slug__iexact=catalog_slug).first()
        catalog_list = Catalog.objects.all()

        # This only works when the catalog request is the primary ID for the DSO
        # So, only Messier and Caldwell.
        raw_dso_list = DSO.objects.filter(catalog__slug=catalog_slug)
        raw_dso_list = raw_dso_list.annotate(cid=Cast('id_in_catalog', IntegerField())).order_by('cid', 'id_in_catalog')
        for x in raw_dso_list:
            x.cat_id = f"{catalog.abbreviation} {x.cid}"
        # deal with C14 = NGC 869 and NGC 884 - both are C 14 but they have two separate
        #   records in the DSO table because the primary IDs have to be unique.
        if catalog_slug == 'caldwell': 
            extra = DSO.objects.filter(catalog__slug='ngc', id_in_catalog__in=['869', '884'])
            extra = extra.annotate(cid=Cast('id_in_catalog', IntegerField())).order_by('cid', 'id_in_catalog')
            for e in extra:
                e.cid = 14
            dso_list = sorted(chain(raw_dso_list, extra), key = attrgetter('cid'))
        elif catalog_slug == 'messier':
            dso_list = raw_dso_list
        else:
            dso_list = assemble_catalog(catalog_slug, raw=raw_dso_list)
        imaged_dso_list =  [x  for x in dso_list if x.num_library_images > 0]
        shown_list = dso_list if all else imaged_dso_list
        
        context['no_alias_catalogs'] = ['caldwell', 'messier']
        context['no_number_catalogs'] = ['other', 'bayer', 'flamsteed']
        context['object_list'] = shown_list
        context['object_count'] = len(dso_list)
        context['image_list_count'] = len(imaged_dso_list)
        context['image_percent'] = 0 if len(dso_list) == 0 else 100. * len(imaged_dso_list) / len(dso_list)
        context['catalog'] = catalog.name
        context['catalog_slug'] = catalog.slug
        context['catalog_list'] = catalog_list
        context['use_title'] = f"{ catalog.name } Images"
        context['constellation_list'] = assemble_constellation_list()
        return context
    
class LibraryConstellationView(TemplateView):
    template_name = 'library_image_list.html'

    def get_context_data(self, **kwargs):
        context = super(LibraryConstellationView, self).get_context_data(**kwargs)
        # Parse abbr from path or from form
        abbr = None
        if 'abbr' in self.kwargs.keys():
            abbr = self.kwargs['abbr']
        abbr = abbr if abbr is not None else self.request.GET.get('abbr', 'AND').upper()
        dso_images = DSOLibraryImage.objects.filter(object__constellation__abbreviation=abbr).order_by('-ut_datetime', 'order_in_list')
        dso_image_list = get_list_of_primary_library_images(dso_images)

        context['abbreviation'] = abbr
        context['image_list'] = dso_image_list
        context['constellation'] = Constellation.objects.filter(abbreviation=abbr).first()
        context['object_count'] = len(dso_image_list)
        context['constellation_list'] = assemble_constellation_list()
        return context