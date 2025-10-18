import datetime as dt, pytz
from ..astro.transform import get_hour_angle
from ..observe.models import ObservingLocation
import time

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
        min_priority = 0.,
        mode = 'I',
        #
        location = None,
        min_alt = 30.,
        max_alt = 90.,
        mask = True,
        gear = None,
        scheduled = False,
        times = None,
        on_dso_list_all = False,
        west_ha_limit = 6.,
        incl_low_culmination = False,
        debug = False,
        min_lunar_distance = None,
    ):

    times = [(time.perf_counter(), 'Start')] if times is None else times

    # 1. sort out time if not sent
    if utdt is None:
        utdt = dt.datetime.now(dt.timezone.utc)
    else:
        if type(utdt) == str:
            utdt = parse_utdt(utdt)
    utdt += dt.timedelta(hours=offset_hours)

    # 2. get location if not sent
    if location is None:
        location = ObservingLocation.get_default_location()
    
    times.append((time.perf_counter(), 'Filtering DSOs'))

    candidate_pks = []

    for d in dsos: # loop on DSOs
        override_active = on_dso_list_all and (d.active_observing_list_count > 0)
        # Filter based on existing images
        priority = d.mode_priority_value_dict[mode]
        if priority is None and not override_active:
            continue
        if (priority != None) and (priority < min_priority) and not override_active:
            continue
        if (priority is None) and override_active:
            pass
        # always include imaged = 'All'
        if imaged == 'Yes' and d.library_image is None:
            continue
        elif imaged == 'Redo':
            if d.library_image is not None and not d.reimage:
                continue
        elif imaged == 'No' and d.library_image is not None and d.reimage == False:
            continue
        # filter by gear
        if (gear is not None) and len(d.mode_list) > 0:
            gear_set = set(gear)
            dso_set = set(d.mode_list)
            n_overlap = len(gear_set.intersection(dso_set))
            if n_overlap < 1:
                continue
        if scheduled and (d.active_observing_list_count == 0):
            continue
        # Is it in a good location in the sky?
        hour_angle = get_hour_angle(utdt, location.longitude, d.ra_float)
        (az, alt, _) = d.alt_az(location, utdt)
        # TODO: Is it far enough away from the Moon
        # Check against location masks, etc.
        in_window = is_available_at_location(location, az, alt, min_alt=min_alt, max_alt=max_alt, use_mask=mask, debug=debug)
        if not in_window:
            continue
        # Is it below the celestial pole?
        if not incl_low_culmination:
            if location.latitude > 0.:   # Northern circumpolar
                if d.dec_float > location.latitude and abs(hour_angle) > 6.0:
                    print(f"Skipping {d} HA: {hour_angle:.2f} Dec: {d.dec_float:.2f}")
                    continue
            else: # Southern circumpolar
                if d.dec_float < location.latitude and abs(hour_angle) > 6.0:
                    print(f"Skipping {d} HA: {hour_angle:.2f} Dec: {d.dec_float:.2f}")
                    continue
        # Is it about to set?
        if west_ha_limit is not None:
            if hour_angle > west_ha_limit: # things are setting - ignore them
                print(f"Setting: {d} HA: {hour_angle:.2f} > {west_ha_limit}")
                continue
        candidate_pks.append(d.pk)
        if debug:
            if alt < min_alt:
                print(f"ERROR WITH DSO {d}: alt = {alt}, in_window = {in_window}")

    times.append((time.perf_counter(), 'Assemble DSO List'))

    # Given the subset of DSOs - assemble the list
    dsos = dsos.filter(pk__in=candidate_pks)
    for d in dsos:
        (az, alt, secz) = d.alt_az(location, utdt)
        d.azimuth = az
        d.altitude = alt
        d.airmass = secz

    return dict(utdt=utdt, dsos=dsos, location=location), times

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
        use_mask=True,
        debug=False
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
    
    if masks.count() > 0:
        for mask in masks:
            if az < mask.azimuth_start or az >= mask.azimuth_end: # not in window
                continue
            # We're in the zone
            mask_alt = interpolate_for_altitude(mask, az)
            return alt >= mask_alt
    
    return True # default if no mask is set for this azimuth...

