from django.db import models
from django.utils.translation import gettext as _

class Planet(models.Model):
    name = models.CharField (
        _('Name'),
        max_length = 20,
    )
    slug = models.SlugField (
        _('Slug'),
        null=True, blank=True
    )
    load = models.CharField (
        _('BSP File Name'),
        max_length = 20,
        null=True, blank=True
    )
    diameter = models.FloatField (
        _('Diameter'),
        help_text = 'Kilometers'
    )
    semi_major_axis = models.FloatField (
        _('Semi-Major Axis'),
        null = True, blank = True,
        help_text = 'au'
    )
    moon_names = models.CharField (
        _('Moon Names'),
        max_length = 100,
        null=True, blank=True,
        help_text = 'List of moons that might be observable; separate with commas'
    )
    @property
    def target(self):
        return "{} Barycenter".format(self.name)

    @property
    def moon_list(self):
        if not self.moon_names:
            return None
        mlist = []
        for m in self.moon_names.split(','):
            mlist.append(m.strip())
        return mlist

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['semi_major_axis']

"""
Moons:
    Ph  vga = 0.07, r = 13.0 x 11.4 x 9.1
    De  vga = 0.08, r = 7.8 x 6.0 x 5.1

    Io  vga = 0.62, r = 1821.5
    Eu  vga = 0.68, r = 1560.8
    Ga  vga = 0.44, r = 2631.2
    Ca  vga = 0.19, r = 2410.3

    Mi  vga = 0.6,  r = 208 x 197 x 191
    En  vga = 1.0,  r = 257 x 251 x 248
    Te  vga = 0.8,  r = 538 x 528 x 526
    Di  vga = 0.7,  r = 563 x 561 x 560
    Rh  vga = 0.7,  r = 765 x 763 x 762
    Ti  vga = 0.22, r = 2575.
    Ia  vga = 0.05 to 0.5, r = 746 x 746 x 712

    Ob  vga = 0.23, r = 761.4
    Ti  vga = 0.27, r = 788.9

    Tr  vga = 0.72, r = 1353.4
"""