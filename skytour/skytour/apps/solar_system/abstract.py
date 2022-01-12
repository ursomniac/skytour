import datetime, pytz
from django.db import models
from django.utils.translation import gettext as _
from ..observe.time import get_julian_date

class OrbitalElements(models.Model):
    """
    I think this works for comets too, so make it an abstract model.
    """
    epoch = models.CharField ( # epoch of the orbital elements
        _('MPC Epoch'),
        max_length = 5,
        null = True, blank = True,
        help_text = 'Epoch of osculation of the orbital elements'
    )
    mean_anomaly = models.FloatField ( # at the epoch
        _('Mean Anomaly')
    )
    arg_perihelion = models.FloatField ( # degrees  J2000.0
        _('Arg. of Perihelion')
    )
    long_asc_node = models.FloatField ( # degrees  J2000.0
        _('Long. of Asc. Node')
    )
    inclination = models.FloatField ( # degrees J2000.0
        _('Inclination')
    )
    eccentricity = models.FloatField (
        _('Eccentricity')
    )
    daily_motion = models.FloatField ( # °/day
        _('Daily Motion')
    )
    semi_major_axis = models.FloatField( # AU
        _('Semi-Major Axis')
    )

    @property
    def get_epoch_utdt(self):
        s = self.epoch
        MONTHS = '123456789ABC'
        DAYS = '123456789ABCDEFGHIJKLMNOPQRSTUV'
        CENTURIES = 'IJK'

        century = CENTURIES.index(s[0])*100 + 1800
        year = int(s[1:3])
        month = MONTHS.index(s[3]) + 1
        day = DAYS.index(s[4]) + 1
        utdt = datetime.datetime(century+year, month, day, 0, 0).replace(tzinfo=pytz.utc)
        return utdt

    @property
    def get_epoch_jd(self):
        utdt = self.get_epoch_utdt()
        return get_julian_date(utdt)

    class Meta:
        abstract = True