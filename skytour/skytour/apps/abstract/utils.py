import datetime as dt
import pytz

from ..astro.time import get_last, get_julian_date
from ..solar_system.position import get_object_metadata
from ..astro.transform import get_alt_az
from ..astro.utils import get_small_sep
from ..misc.models import TimeZone
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
            raw_ang = ephem['observe']['angular_diameter']
            angular_diameter = raw_ang * 3600. # arcsec
            ang_diam_units = '\"'
            ra = ephem['apparent']['equ']['ra']
            dec = ephem['apparent']['equ']['dec']
            distance = ephem['apparent']['distance']['au']
            distance_units = 'AU'
            constellation = ephem['observe']['constellation']['abbr']
            apparent_magnitude = ephem['observe']['apparent_magnitude']
        except:
            return None
    else:
        ra = target.ra_float
        dec = target.dec_float
        distance = target.distance
        distance_units = target.distance_units
        constellation = target.constellation.abbreviation
        angular_diameter = target.major_axis_size # arcmin
        ang_diam_units = '\''
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
        ang_diam_units = ang_diam_units,
        apparent_magnitude = apparent_magnitude,
        altitude = altitude,
        azimuth = azimuth,
        sec_z = airmass,
        hour_angle = hour_angle,
        julian_date = julian_date,
        sidereal_time = last
    )
    return d

def get_real_time_conditions(target, request, context, debug=False):
    errors = False
    utdt = None
    dt_base = request.GET.get('utdt_base', 'now')
    text_offset = request.GET.get('offset', '0.')
    offset = float(text_offset) if text_offset else 0.
    lunar_distance = None
    if debug:
        print(f"DT BASE: {dt_base} OFFSET: {offset}")
    # Set up datetimes
    utdt = dt.datetime.now().replace(tzinfo=pytz.utc) if dt_base == 'now' else context['utdt_start']
    utdt += dt.timedelta(hours=offset)

    if dt_base == 'cookie':
        local_time = context['local_time'] + dt.timedelta(hours=offset)
        time_zone = 'UTC'
    else:
        time_zone_id = find_site_parameter('default-time-zone-id', 2, 'positive')
        time_zone = TimeZone.objects.get(pk=time_zone_id).name
        local_time = utdt.astimezone(pytz.timezone(time_zone))

    # STUPID BUG IN DJANGO - AFAICT the |date template tag ALWAYS goes back to the
    #   System time zone, so local_time will ALWAYS BE in UTC
    local_time_str = local_time.strftime("%Y-%b-%d %H:%M:%S")

    if debug:
        print(f"TZ: {time_zone}")
        print(f"UT: {utdt}")
        print(f"LOCAL: {local_time}")

    # Set up location
    if dt_base == 'cookie':
        location = context['location']
    else:
        location_id = find_site_parameter('default-location-id', default=48, param_type='positive'),
        location = ObservingLocation.objects.filter(pk=location_id[0]).first()

    #if dt_base == 'cookie':
    try:    
        moon = context['cookies']['moon']
        moon_ra = moon['apparent']['equ']['ra']
        moon_dec = moon['apparent']['equ']['dec']
        (moon_az, moon_alt, moon_airmass) = get_alt_az(utdt, location.latitude, location.longitude, moon_ra, moon_dec)
        #print(f"AZ: {moon_az} ALT: {moon_alt} AIR: {moon_airmass}")
        if moon_alt > -10.:
            lunar_distance = get_small_sep(moon_ra, moon_dec, target.ra_float, target.dec_float)
    except:
        print("Cannot find moon")
        
    last = get_last(utdt, location.longitude)
    object_type = target._meta.model_name
    if object_type == 'dso':
        ra = target.ra_float
        dec = target.dec_float
        distance = target.distance
        distance_units = target.distance_units
        constellation = target.constellation.abbreviation
        angular_diameter = target.major_axis_size  # arcsec
        angular_diameter_units = '\''
        apparent_magnitude = target.magnitude
        surface_brightness = target.surface_brightness
        max_alt = target.max_altitude(location=location)
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
            max_alt = 90. - location.latitude + dec
            max_alt = 180 - max_alt if max_alt > 90 else max_alt
            distance = ephem['apparent']['distance']['au']
            distance_units = 'AU'
            constellation = ephem['observe']['constellation']['abbr']
            if object_type != 'comet':
                angular_diameter = ephem['observe']['angular_diameter'] * 3600. # arcsec
                angular_diameter_units = '\"'
            else:
                angular_diameter = None
                angular_diameter_units = None
            apparent_magnitude = ephem['observe']['apparent_magnitude']
            surface_brightness = None
        except:
            errors = True

    
    if utdt and location and not errors:
        azimuth, altitude, airmass = get_alt_az(utdt, location.latitude, location.longitude, ra, dec)
        hour_angle = rectify_ha(last - ra)
        julian_date = get_julian_date(utdt)
        
        d = dict(
            utdt = utdt,
            local_time = local_time,
            local_time_str = local_time_str,
            location = location,
            ra = ra,
            dec = dec,
            distance = distance,
            distance_units = distance_units,
            constellation = constellation,
            angular_diameter = angular_diameter,
            angular_diameter_units = angular_diameter_units,
            apparent_magnitude = apparent_magnitude,
            surface_brightness = surface_brightness,
            altitude = altitude,
            azimuth = azimuth,
            sec_z = airmass,
            hour_angle = hour_angle,
            julian_date = julian_date,
            sidereal_time = last,
            display_name = target.__str__(),
            max_alt = max_alt,
            lunar_distance = lunar_distance
        )
        context['real_time'] = d
        context['use_date'] = dt_base
        context['use_offset'] = offset
    return context
