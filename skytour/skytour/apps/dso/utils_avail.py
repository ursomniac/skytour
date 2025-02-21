import datetime as dt, pytz
from ..observe.models import ObservingLocation
from ..site_parameter.helpers import find_site_parameter

# NOTE: This is in its own app mostly to get around a circular import problem.

def parse_utdt(s):
    """
    Return datetime from formatted string of time.
    """
    utdt = None
    if s is None or len(s.strip()) == 0:
        return None
    has_sec = len(s.split(':')) == 3
    fmt = '%Y-%m-%d %H:%M' 
    fmt += ':%S' if has_sec else ''
    try:
        utdt = dt.datetime.strptime(s, fmt).replace(tzinfo=pytz.utc)
        return utdt
    except:
        print("PARSE ERROR: ", s)
        return None
    
def find_dsos_at_location_and_time (
        dsos = None,
        utdt = None, # set to now if none 
        offset_hours = 0., 
        imaged = 'No',
        min_priority = 0,
        #
        location = None,
        min_alt = 30.,
        max_alt = 90.,
        min_dec = None,
        max_dec = None,
        mask = True,
        gear = None,
        scheduled = False
    ):

    # 1. sort out time if not sent
    if utdt is None:
        utdt = dt.datetime.now(dt.timezone.utc)
    else:
        if type(utdt) == str:
            utdt = parse_utdt(utdt)
    utdt += dt.timedelta(hours=offset_hours)

    # 2. get location if not sent
    if location is None:
        location_id = find_site_parameter('default-location-id', default=1, param_type='positive')
        location = ObservingLocation.objects.get(pk=location_id)
        
    candidate_pks = []
    for d in dsos: # loop on DSOs
        # Filter based on existing images
        if d.imaging_checklist_priority is None:
            continue
        if d.imaging_checklist_priority < min_priority:
            continue
        # always include imaged = 'All'
        if imaged == 'Yes' and d.library_image is None:
            continue
        elif imaged == 'Redo':
            if d.library_image is not None and not d.reimage:
                continue
        elif imaged == 'No' and d.library_image is not None and d.reimage == False:
            continue
        if gear is not None and len(d.targetdso.mode_list) > 0:
            gear_set = set(gear)
            dso_set = set(d.targetdso.mode_list)
            n_overlap = len(gear_set.intersection(dso_set))
            if n_overlap < 1:
                continue
        if scheduled and d.active_observing_list_count == 0:
            continue
        (az, alt, _) = d.alt_az(location, utdt)
        in_window = is_available_at_location(location, az, alt, min_alt=min_alt, max_alt=max_alt, use_mask=mask)
        if in_window:
            candidate_pks.append(d.pk)
    
    # Given the subset of DSOs - assemble the list
    dsos = dsos.filter(pk__in=candidate_pks)
    for d in dsos:
        (az, alt, secz) = d.alt_az(location, utdt)
        d.azimuth = az
        d.altitude = alt
        d.airmass = secz

    return dict(utdt=utdt, dsos=dsos, location=location)

def assemble_gear_list(request):
    out = ""
    for g in 'NBSMI':
        name = f"gear{g}"
        out += request.GET.get(name, '')
    return out if len(out) > 0 else None

def is_available_at_location (
        location,               # ObservingLocation object 
        az, alt,                # Object's azimuth and altitude
        min_alt=10.,            # Absolute minimum altitude (can be overridden)
        max_alt=90,             # Absolute maximum altitude (can be overridden)
        use_mask=True
    ):
    """
    See if an object's azimuth and altitude are above the mask set for a location.
    """

    def interpolate_for_altitude(m, az):
        """
        Given two mask endpoints, get the altitude for a given mask and azimuth
        This is an internal method
        """
        if m.altitude_end == m.altitude_start: # Flat so constant
            return m.altitude_start
        # Deal with azimuth
        daz = m.azimuth_end - m.azimuth_start # size of az window
        faz = az - m.azimuth_start  # degrees into window 
        paz = faz/daz # percentage
        # Deal with altitude
        dalt = m.altitude_end - m.altitude_start # change in altitude
        alt = m.altitude_start + paz * dalt
        return alt

    # Deal with no location or no masks
    if location is None: # Shouldn't get here - but assume True
        return True 
        
    masks = location.observinglocationmask_set.all()
    if masks.count() == 0: # Oops - no masks defined for this location!  Assume True
        return True
        
    # Stupid - but ... deal with bogus values
    if abs(alt) > 90. or az < 0:
        return False
    az %= 360.

    # Global restrictions - too low or too high
    if max_alt is not None and alt > max_alt:
        return False
    if min_alt is not None and alt < min_alt:
        return False
    
    # OK - play with the masks
    if not use_mask:
        return True
    
    for mask in masks:
        if az < mask.azimuth_start or az >= mask.azimuth_end: # not in window
            continue
        # We're in the zone
        mask_alt = interpolate_for_altitude(mask, az)
        return alt >= mask_alt
    
    return True # default if no mask is set for this azimuth...