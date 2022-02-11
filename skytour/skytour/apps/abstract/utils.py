import math
from ..observe.time import get_last, get_julian_date
from ..utils.transform import get_alt_az

def rectify_ha(xha):
    if xha <= -12.:
        return xha + 24.
    if xha >= 12:
        return xha - 24.
    return xha

def get_metadata(observation, ephem=None):
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

    if observation.object_type != 'DSO' and ephem is not None:
        ra = ephem['coords']['ra']
        dec = ephem['coords']['dec']
        distance = ephem['coords']['distance']['au']
        distance_units = 'AU'
        constellation = ephem['observe']['constellation']['abbr']
        angular_diameter = ephem['observe']['angular_diameter']
        apparent_magnitude = ephem['observe']['apparent_mag']
    else:
        ra = target.ra_float
        dec = target.dec_float
        distance = target.distance
        distance_units = target.distance_units
        constellation = target.constellation.abbreviation
        angular_diameter = target.major_axis_size * 60. # arcsec
        apparent_magnitude = target.magnitude

    azimuth, altitude = get_alt_az(utdt, location.latitude, location.longitude, ra, dec)
    sec_z = 1./math.cos(math.radians(90-altitude))
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
        sec_z = sec_z,
        hour_angle = hour_angle,
        julian_date = julian_date,
        sidereal_time = last
    )
    return d
    
