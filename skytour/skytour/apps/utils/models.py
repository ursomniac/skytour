from django.db import models
from django.utils.translation import gettext as _
from ckeditor.fields import RichTextField
from colorfield.fields import ColorField
from ..plotting.vocabs import MAP_SYMBOL_TYPES

class AbstractCatalog(models.Model):
    name = models.CharField (
        _('Catalog Name'),
        max_length = 100
    )
    slug = models.SlugField (
        _('Slug')
    )
    abbreviation = models.CharField (
        _('Abbreviation'),
        max_length = 10
    )
    use_abbr = models.BooleanField (
        _('Use Abbr in List'),
        default = True
    )
    description = models.TextField (
        _('Description'),
        null=True, blank=True
    )

    class Meta:
        abstract = True

class Catalog(AbstractCatalog):
    """
    One Catalog is Proper Name - it has an empty abbreviation.
    """

    def filter_dso_list(self, filters=None):
        dso_list = self.dso_list
        flist = []
        for dso in dso_list:
            if 'seen' in filters and dso.observations.count() == 0:
                continue
            if 'important' in filters and dso.priority not in ['High', 'Highest']:
                continue
            if 'unseen' in filters and dso.observations.count() != 0:
                continue
            if 'available' in filters and dso.priority == 'None':
                continue
            flist.append(dso)
        return flist

    @property
    def dso_count(self):
        """
        You need this separately because membership can be through a primary id OR an alias.
        """
        return self.dso_set.count() + self.dsoalias_set.count()

    @property
    def dso_list(self):
        dso1 = self.dso_set.order_by('id_in_catalog')
        dso2 = self.dsoalias_set.annotate(
            iic=models.functions.Cast('id_in_catalog', models.IntegerField())
        ).order_by('iic')
        dsos = []
        for dso in dso1:
            dsos.append(dso)
        for dso in dso2:
            dsos.append(dso.object)
        return dsos

    @property
    def observing_stats(self):
        n_total = 0
        n_obs = 0
        n_imaged = 0
        n_available = 0
        for dso in self.dso_list:
            n_total += 1
            if dso.number_of_observations > 0:
                n_obs += 1
            if dso.priority != 'None':
                n_available += 1
            n_imaged += 1 if dso.num_library_images > 0 else 0
        
        f_obs = (n_obs + 0.)/n_total
        f_avail = (n_obs + 0.)/n_available
        return dict(
            n_obs=n_obs,
            n_imaged=n_imaged,
            p_imaged = 100.* (n_imaged + 0.)/n_total,
            p_img_available = 100.* (n_imaged + 0.)/n_available,
            n_total=n_total,
            f_obs=f_obs,
            p_obs=f_obs*100.,
            n_available=n_available,
            f_available=f_avail,
            p_available=f_avail*100.

        )

    class Meta:
        ordering = ['abbreviation']
        verbose_name = 'DSO Catalog'
        verbose_name_plural = 'DSO Catalogs'

    def get_absolute_url(self):
        return '/catalog/{}'.format(self.pk)

    def __str__(self):
        return self.abbreviation

class StarCatalog(AbstractCatalog):
    pass


class ObjectType(models.Model):
    """
    DSO Object Types
    """
    name = models.CharField(
        _('Name'),
        max_length = 200
    )
    slug = models.SlugField(
        _('Slug'),
        unique = True
    )
    short_name = models.CharField (
        _('Short Name'),
        max_length = 40,
        null = True, blank = True
    )
    bgcolor = ColorField (
        _('Background Color'),
        default = '#666666'
    )
    # need icon field
    marker_type = models.CharField(
        _('Plot Marker Type'),
        max_length = 10,
        default = 'x'
    )
    marker_color = models.CharField(
        _('Marker Type Color'),
        max_length = 7,
        default = '#999'
    )
    map_symbol_type = models.CharField(
        _('Map Symbol Type'),
        choices = MAP_SYMBOL_TYPES,
        max_length = 30,
        default = 'marker'
    )
    code = models.CharField(
        _('Abbr. Code'),
        max_length = 4,
        null = True, blank = True
    )

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']

class Constellation(models.Model):
    """
    CV of the constellations.
    """
    name = models.CharField(
        _('Name'),
        max_length = 80
    )
    abbreviation = models.CharField (
        _('Abbreviation'),
        max_length = 3
    )
    slug = models.SlugField (
        _('Slug'),
        #unique = True
        default = 'xxx'
    )
    genitive = models.CharField (
        _('Genitive'),
        max_length = 80
    )
    map = models.ImageField (
        _('Map'),
        upload_to = 'constellation_maps',
        null=True, blank=True
    ) 
    other_map = models.ImageField ( # This ONLY exists because of Serpens
        _('Other Map'),
        upload_to = 'constellation_maps',
        null=True, blank=True
    )
    background = RichTextField (
        _('Background'),
        null = True, blank = True
    )
    historical_image = models.ImageField (
        _('Historical Map'),
        upload_to = 'historical_constellation_maps',
        null = True, blank = True
    )
    neighbors = models.ManyToManyField (
        'self',
        blank = True
    )
    center_ra = models.FloatField ('Center RA')
    center_dec = models.FloatField('Center Dec.')
    area = models.FloatField('Area', help_text='sq. Deg.')

    @property
    def abbr_case(self):
        exceptions = {
            'CMA': 'CMa', 'CMI': 'CMi', 'CRA': 'CrA', 'CRB': 'CrB',
            'CVN': 'CVn', 'LMI': 'LMi', 'PSA': 'PsA', 'TRA': 'TrA',
            'UMA': 'UMa', 'UMI': 'UMi'
        }
        if self.abbreviation in exceptions.keys():
            return exceptions[self.abbreviation]
        return self.abbreviation.title()

    @property
    def atlas_plate_list(self):
        pp = []
        for p in self.atlasplate_set.order_by('plate_id'):
            pp.append(str(p.plate_id))
        return ', '.join(pp)
    
    @property
    def dso_in_field_count(self):
        return self.dsoinfield_set.count()

    def get_absolute_url(self):
        return '/constellation/{}'.format(self.slug)

    class Meta:
        ordering = ['abbreviation']

    def __str__(self):
        return self.abbreviation

    def save(self, *args, **kwargs):
        self.slug = self.abbreviation
        super(Constellation, self).save(*args, **kwargs)

class ConstellationVertex(models.Model):
    """
    pk is the vertex ID.
    """
    ra_1875 = models.FloatField(_('R.A. 1875'))
    dec_1875 = models.FloatField(_('Dec. 1875'))
    constellation = models.ManyToManyField (Constellation)

class ConstellationBoundaries(models.Model):
    start_vertex = models.PositiveIntegerField('Start Vertex')
    end_vertex = models.PositiveIntegerField('End Vertex')
    ra = models.FloatField(_('Start R.A.'))
    dec = models.FloatField(_('Start Dec.'))
