
from django.db import models
from django.utils.translation import gettext as _
from numpy import True_
from skyfield.api import Star
from ..utils.models import (
    Coordinates, 
    Constellation
) 
from .utils import create_star_name, parse_designation

class DoubleStar(Coordinates):
    constellation = models.ForeignKey (Constellation, 
        on_delete=models.PROTECT,
        null = True, blank = True
    )
    separation = models.FloatField(
        _('Ang. Sep'),
        help_text = 'Arcseconds'
    )
    magnitudes = models.CharField(
        _('Magnitudes'),
        max_length = 100,
        help_text = 'comma separated'
    )
    spectral_type = models.CharField (
        _('Spectral Type'),
        max_length = 100
    )
    notes = models.TextField (
        _('Notes'),
        null = True, blank = True
    )

    @property
    def get_magnitudes(self):
        str_mags = self.magnitudes.split(',')
        mags = []
        for star in str_mags:
            mags.append(float(star))

class DoubleStarAlias(models.Model):
    object = models.ForeignKey(DoubleStar, 
        on_delete=models.CASCADE,
        related_name='aliases'
    )
    catalog = models.ForeignKey('utils.Catalog', on_delete = models.CASCADE)
    id_in_catalog = models.CharField (
        _('ID'),
        max_length = 24
    )

class BrightStar(Coordinates):
    """
    Bright Star Catalog data
    """
    hr_id = models.PositiveIntegerField(_('HR #'))
    bayer = models.CharField(_('Bayer'), max_length=10, null=True, blank=True)
    flamsteed = models.CharField(_('Flamsteed'), max_length=10, null=True, blank=True)
    constellation = models.CharField(_('Constellation'), 
        max_length = 3,
        null = True, blank = True
    )
    bd_id = models.CharField(_('BD #'), max_length=11, null = True, blank = True)
    hd_id = models.PositiveIntegerField( _('HD #') ,  null=True, blank=True)
    sao_id = models.PositiveIntegerField(_ ('SAO #'), null=True, blank=True)
    fk5_id = models.PositiveIntegerField( _('FK5 #'), null=True, blank=True)
    double_star = models.CharField(_('Double Star Code'), max_length=1, blank=True, null=True)
    ads_id = models.CharField(_('ADS Designation'), max_length=5, null=True, blank=True)
    var_id = models.CharField(_('Var. Star ID'), max_length=9, null=True, blank=True)
    # ra_h, ra_m, ra_s, dec_sign, dec_d, dec_m, dec_s in Coordinate abstract class 
    gal_long = models.FloatField(_('Gal. Long.'), blank=True, null=True)
    gal_lat = models.FloatField(_('Gal. Lat.'), null=True, blank=True)
    magnitude = models.FloatField(_('V Mag.'), blank=True, null=True)
    b_v = models.FloatField(_('B-V'), null=True, blank=True)
    u_b = models.FloatField(_('U-B'), null=True, blank=True)
    r_i = models.FloatField(_('R-I'), null=True, blank=True)
    spectral_type = models.CharField(_('Spectral Type'), max_length=20, null=True, blank=True)
    spt_code = models.CharField(_('Sp. Type Code'), max_length=1, null=True, blank=True)
    pm_ra = models.FloatField(_('Prop. Motion RA'), null=True, blank=True)
    pm_dec = models.FloatField(_('Prop. Motion Dec.'), null=True, blank=True)
    parallax_flag = models.CharField(_('Parallax Flag'), max_length=1, null=True, blank=True)
    parallax = models.FloatField(_('Parallax'), null=True, blank=True)
    radial_velocity = models.FloatField(_('Radial Velocity'), null=True, blank=True)
    rv_flag = models.CharField(_('RV Flag'), max_length=1, null=True, blank=True)
    rot_flag = models.CharField(_('Rot. Vel. Flag'), max_length=2, null=True, blank=True)
    vsini = models.PositiveIntegerField(_('v sin i'), null=True, blank=True)
    d_mag = models.FloatField(_('d Mag (double)'), null=True, blank=True)
    ang_sep = models.FloatField(_('Ang. Sep.'), null=True, blank=True)
    notes = models.BooleanField(_('Notes'), default=False)
    name = models.CharField(_('Name'), max_length=40, null=True, blank=True )
    

    @property
    def skyfield_object(self):
        return Star(ra_hours=self.ra_float, dec_degrees=self.dec_float)

    @property
    def plot_label(self):
        if not self.name:
            return None
        first = self.name.split(' ')[0]
        if first.isdecimal():
            return first
        # else it has a letter or a greek letter and possibly a number
        return parse_designation(first)

    def save(self, *args, **kwargs):
        self.ra = self.ra_float # get from property
        self.dec = self.dec_float # get from property
        self.ra_text = self.format_ra # get from property
        self.dec_text = self.format_dec # get from property
        self.name = create_star_name(self)
        super(BrightStar, self).save(*args, **kwargs)