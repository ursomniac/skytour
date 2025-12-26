from django.db import models
from django.utils.translation import gettext as _
from colorfield.fields import ColorField
from ..abstract.models import WikipediaPage, WikipediaPageObject
from ..abstract.vocabs import YES_NO, NO
from ..plotting.vocabs import MAP_SYMBOL_TYPES
from .vocabs import CATALOG_PRECEDENCE, CATALOG_LOOKUP_CHOICES

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

    expected_complete = models.PositiveIntegerField ( 
        # Are all the entries in the Catalog expected to be in the DSO/DSOInField models?
        # e.g., Messier and Caldwell = Yes;  NGC and IC = No
        _('Expected Completed'),
        choices = YES_NO,
        default = NO
    )
    description = models.TextField (
        _('Description'),
        null=True, blank=True
    )
    number_objects = models.PositiveIntegerField (
        _('Number of Objects'),
        null = True, blank = True,
        help_text = 'Might include missing/invalid objects'
    )
    notes = models.TextField (
        _('Notes'),
        null = True, blank = True
    )
    precedence = models.PositiveIntegerField (
        # Precedence = 1 - 9
        #  1. Primary (Caldwell, Messier)
        #  2. Important (NGC, IC)
        #  3. Secondary (B, Cr, Mel, Sh2)
        #  4. Collection (Ab, Arp, HCG, Stock, Tr, vdB)
        #  5. Ancillary (H400)
        #  6. Survey (LBN, LDN, PGC, PK, UGC)
        #  7. Other (other)
        #  8. Incidental (Bayer, Flamsteed)
        #  9. Custom (Ast24, Ast)
        _('Precedence in Catalog Lists'),
        null = True, blank = True,
        choices = CATALOG_PRECEDENCE
    )

    @property
    def sortable_precedence(self):
        return f"{self.precedence:02d}-{self.slug}"

    class Meta:
        abstract = True

class Catalog(AbstractCatalog):
    """
    One Catalog is Proper Name - it has an empty abbreviation.
    """
    lookup_mode = models.CharField (
        _('Lookup Mode'),
        max_length = 40,
        choices = CATALOG_LOOKUP_CHOICES,
        default = 'abbreviation',
        help_text = 'for lookups like Wikipedia'
    )

    @property
    def dso_count(self):
        """
        You need this separately because membership can be through a primary id OR an alias.
        """
        return self.dso_set.count() + self.dsoalias_set.count()

    @property
    def dso_list(self):  # Used below
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
        """
        Count up # observed/images and % observed/imaged
        """
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
        ordering = ['precedence', 'abbreviation']
        verbose_name = 'DSO Catalog'
        verbose_name_plural = 'DSO Catalogs'

    def get_absolute_url(self):
        return '/catalog/{}'.format(self.pk)

    def __str__(self):
        return self.abbreviation

class StarCatalog(AbstractCatalog):
    pass

    def __str__(self):
        return f"{self.abbreviation} = {self.name}"

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

class FormerConstellation(models.Model):
    """
    Former constellations
    """
    name = models.CharField (
        _('Name'),
        max_length = 200
    )
    slug = models.SlugField (
        _('Slug'),
        max_length = 3
    )
    source = models.TextField (
        _('Source'),
        null = True, blank = True
    )
    year = models.PositiveIntegerField (
        _('Year'),
        null = True, blank = True
    )


    @property
    def abbreviation(self):
        return self.slug

class Constellation(WikipediaPageObject, models.Model):
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
    description = models.TextField (
        _('Description'),
        null = True, blank = True,
        help_text = 'Can contain raw HTML'
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
        # Return case-sensitive constellation abbreviation
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
        # Return list of atlas plates that contain part of the constellation
        pp = []
        for p in self.atlasplate_set.order_by('plate_id'):
            pp.append(str(p.plate_id))
        return ', '.join(pp)
    
    @property
    def dso_in_field_count(self):
        return self.dsoinfield_set.count()
    
    @property
    def dsos_with_library_images(self):
        return self.dso_set.annotate(n=models.Count('image_library')).filter(n__gte=1)
    
    @property
    def count_dsos_with_library_images(self):
        return self.dsos_with_library_images.count()
    
    @property
    def default_wikipedia_name(self):
        return f"{self.name}_(constellation)"

    def get_absolute_url(self):
        return '/constellation/{}'.format(self.slug)

    class Meta:
        ordering = ['abbreviation']

    def __str__(self):
        return self.abbreviation

    def save(self, *args, **kwargs):
        self.slug = self.abbreviation
        super(Constellation, self).save(*args, **kwargs)


class ConstellationWiki(WikipediaPage):
    object = models.OneToOneField(
        Constellation, 
        on_delete=models.CASCADE,
        primary_key = True,
        related_name = 'wiki'
    )


class ConstellationVertex(models.Model):
    """
    pk is the vertex ID.

    List of constellation boundary coordinates.
    NOTE: All values are Epoch 1875 for (ra, dec) - must be precessed for plotting!
    """
    ra_1875 = models.FloatField(_('R.A. 1875'))
    dec_1875 = models.FloatField(_('Dec. 1875'))
    constellation = models.ManyToManyField (Constellation)

class ConstellationBoundaries(models.Model):
    """
    List of vertices to make up a constellation boundary.
    """
    start_vertex = models.PositiveIntegerField('Start Vertex')
    end_vertex = models.PositiveIntegerField('End Vertex')
    ra = models.FloatField(_('Start R.A.'))
    dec = models.FloatField(_('Start Dec.'))
