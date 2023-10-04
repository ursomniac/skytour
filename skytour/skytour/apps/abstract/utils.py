import datetime as dt
import pytz

from ..astro.time import get_last, get_julian_date
from ..solar_system.position import get_object_metadata
from ..astro.transform import get_alt_az
from ..site_parameter.helpers import find_site_parameter
from ..observe.models import ObservingLocation

def rectify_ha(xha):
    if xha <= -12.:
        return xha + 24.
    if xha >= 12:
        return xha - 24.
    return xha

def get_metadata(observation):
    """
    For the set of observables:
        Planet
        Asteroid
        Comet
        DSO 

    Get the position information and return:
        Altitude
        Azimuth
        Hour Angle
        Airmass
        Constellation
        If not DSO:
            RA
            Dec
            Distance
            Angular Diameter
    """
    utdt = observation.ut_datetime
    target = observation.object
    location = observation.location
    last = get_last(utdt, location.longitude)
    object_type = observation.object_type

    if observation.object_type != 'DSO':
        if object_type == 'Planet':
            eph_label = target.target
        else:
            eph_label = None

        ephem = get_object_metadata(
            utdt, 
            eph_label, 
            object_type.lower(), 
            instance=target, 
            location=location
        )
        try:
            ra = ephem['apparent']['equ']['ra']
            dec = ephem['apparent']['equ']['dec']
            distance = ephem['apparent']['distance']['au']
            distance_units = 'AU'
            constellation = ephem['observe']['constellation']['abbr']
            angular_diameter = ephem['observe']['angular_diameter']
            apparent_magnitude = ephem['observe']['apparent_magnitude']
        except:
            return None
    else:
        ra = target.ra_float
        dec = target.dec_float
        distance = target.distance
        distance_units = target.distance_units
        constellation = target.constellation.abbreviation
        angular_diameter = target.major_axis_size * 60. # arcsec
        apparent_magnitude = target.magnitude

    azimuth, altitude, airmass = get_alt_az(utdt, location.latitude, location.longitude, ra, dec)
    hour_angle = rectify_ha(last - ra)
    julian_date = get_julian_date(utdt)

    d = dict(
        ra = ra,
        dec = dec,
        distance = distance,
        distance_units = distance_units,
        constellation = constellation,
        angular_diameter = angular_diameter,
        apparent_magnitude = apparent_magnitude,
        altitude = altitude,
        azimuth = azimuth,
        sec_z = airmass,
        hour_angle = hour_angle,
        julian_date = julian_date,
        sidereal_time = last
    )
    return d
    
def get_real_time_conditions(target, utdt=None, location=None):
    
    utdt = dt.datetime.now() if utdt is None else utdt
    utdt = utdt.replace(tzinfo=pytz.utc)
    if location is None:
        location_id = find_site_parameter('default-location-id', default=48, param_type='positive'),
        location = ObservingLocation.objects.filter(pk=location_id[0]).first()
        if location is None:
            return None
    last = get_last(utdt, location.longitude)
    object_type = target._meta.model_name
    if object_type == 'dso':
        ra = target.ra_float
        dec = target.dec_float
        distance = target.distance
        distance_units = target.distance_units
        constellation = target.constellation.abbreviation
        angular_diameter = target.major_axis_size * 60. # arcsec
        apparent_magnitude = target.magnitude
    else:
        eph_label =  target.target if object_type == 'planet' else None
        ephem = get_object_metadata(
            utdt, 
            eph_label, 
            object_type.lower(), 
            instance=target, 
            location=location
        )
        try:
            ra = ephem['apparent']['equ']['ra']
            dec = ephem['apparent']['equ']['dec']
            distance = ephem['apparent']['distance']['au']
            distance_units = 'AU'
            constellation = ephem['observe']['constellation']['abbr']
            angular_diameter = ephem['observe']['angular_diameter']
            apparent_magnitude = ephem['observe']['apparent_magnitude']
        except:
            return None
        
    azimuth, altitude, airmass = get_alt_az(utdt, location.latitude, location.longitude, ra, dec)
    hour_angle = rectify_ha(last - ra)
    julian_date = get_julian_date(utdt)
    
    d = dict(
        ra = ra,
        dec = dec,
        distance = distance,
        distance_units = distance_units,
        constellation = constellation,
        angular_diameter = angular_diameter,
        apparent_magnitude = apparent_magnitude,
        altitude = altitude,
        azimuth = azimuth,
        sec_z = airmass,
        hour_angle = hour_angle,
        julian_date = julian_date,
        sidereal_time = last,
        display_name = target.__str__()
    )
    return d