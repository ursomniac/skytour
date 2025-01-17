import datetime as dt, pytz
from ..dso.models import DSO
from ..observe.models import ObservingLocation

def parse_utdt(s):
    utdt = None
    if s is None or len(s.strip()) == 0:
        #print(f"GOT NOTHING: [{s}]")
        return None
    has_sec = len(s.split(':')) == 3
    fmt = '%Y-%m-%d %H:%M' 
    fmt += ':%S' if has_sec else ''
    try:
        utdt = dt.datetime.strptime(s, fmt).replace(tzinfo=pytz.utc)
        #print("GOT: ", utdt)
        return utdt
    except:
        print("PARSE ERROR: ", s)
        return None
    
def is_in_window(location_id, az, alt, min_alt=10., max_alt=90, house=False, house_extra=False):
    min_alts = dict(
        neighbor = 40., # above neighbor roof
        street = 30. # in SE hole
    )
    
    if location_id is None:
        return True
    if location_id != 1:
        return alt >= min_alt and alt <= max_alt

    if alt > max_alt:
        return False
    if alt < min_alt:
        return False
    
    if house: # observing from backyard
        if alt > 70 and alt < max_alt: # overhead-ish
            return True
        if az < 120.: # house in the way
            return False
        if az >= 120. and az <= 160. and alt < min_alts['street']: # too low
            return False
        if az >= 160. and az <= 210. and alt < min_alts['neighbor']: # behind neighbor
            return False
        if house_extra: # can we use the SW hole?
            if az >= 210. and az < 230.:
                if alt >= 15. and alt <= 30.: # in hole
                    return True
                elif alt >= 30. and alt <= 50.: # tree
                    return False
            elif az > 230.: # in trees
                return False
        else:
            if az >= 210.: # in trees
                return False
    #else:
    #    if az >= 210.:
    #        return False
    return True
    
def find_objects_at_home(
        utdt = None, # set to now if none 
        offset_hours = 0., 
        imaged = False,
        min_priority = 0,
        #
        location_id = 1,
        min_dec = -20.,
        min_alt = 30.,
        max_alt = 90.,
        house = False,
        scheduled = False
    ):
    """
    This really only works for my back yard, but the logic would pertain for anyone who 
    would want to design a similar function.

    What you need:
        1. distribution of azimuth vs. altitude of obstructions
        2. sidereal time at any point.
    """
    # 1. sort out time
    if utdt is None:
        utdt = dt.datetime.now().replace(tzinfo=pytz.utc)
    else:
        utdt = parse_utdt(utdt)
    utdt += dt.timedelta(hours=offset_hours)
    # 2. get latitude/longitude
    loc =  ObservingLocation.objects.get(pk=location_id)
    # 3. get DSOs
    dsos = DSO.objects.filter(dec__gte=min_dec)

    #candidates = []
    candidate_pks = []
    for d in dsos:
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
        # on active observing list
        if scheduled and d.active_observing_list_count == 0:
            continue

        (az, alt, _) = d.alt_az(loc, utdt)
        use = is_in_window(location_id, az, alt, 
                house=house, min_alt=min_alt, max_alt=max_alt, house_extra=house)
        if use:
            candidate_pks.append(d.pk)

        """
        if alt > 70.: # keep!
            #candidates.append(d)
            candidate_pks.append(d.pk)
            continue
        elif az < 120.:
            continue
        elif az > 230.: 
            continue
        elif az > 160. and az <= 210.: # Kim's house
            #skim = 30. + 15. * (az - 160.) / 70.
            skim = 45.
            if alt < skim:
                continue
        elif az > 210 and az <= 230: # window in the SE
            if alt < 15. or (alt >= 30. and alt <= 60.):
                continue
        elif alt < min_alt: 
            continue
        # in the window!
        candidate_pks.append(d.pk)
        """
    # Return as a queryset 
    # Ideally this should ALSO contain alt/az!
    dsos = DSO.objects.filter(pk__in=candidate_pks)
    for d in dsos:
        (az, alt, secz) = d.alt_az(loc, utdt)
        d.azimuth = az
        d.altitude = alt
        d.airmass = secz
    return dict(utdt=utdt, dsos=dsos, location=loc)

def find_objects_at_cookie(        
        utdt = None, # set to now if none 
        offset_hours = 0., 
        imaged = 'No',
        min_priority = 0,
        #
        location = None,
        min_dec = -30.,
        min_alt = 30.,
        max_alt = 90.,
        house = False,
        gear = None,
        scheduled = False
    ):

    print("GOT HERE AT COOKIE")
    print("MIN DEC: ", min_dec, " HOUSE: ", house)
    # 1. sort out time
    if utdt is None:
        utdt = dt.datetime.now().replace(tzinfo=pytz.utc)
    else:
        if type(utdt) == str:
            utdt = parse_utdt(utdt)
    utdt += dt.timedelta(hours=offset_hours)
    # 2. get latitude/longitude
    if location is None:
        loc = ObservingLocation.objects.get(pk=1)
    else:
        loc = location
    # 3. get DSOs
    dsos = DSO.objects.filter(dec__gte=min_dec)

    candidate_pks = []
    for d in dsos:
        
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
        (az, alt, _) = d.alt_az(loc, utdt)
        in_window = is_in_window(
                loc.id, az, alt, house=house, 
                min_alt=min_alt, max_alt=max_alt, house_extra=house
            )
        if in_window:
            candidate_pks.append(d.pk)

    dsos = DSO.objects.filter(pk__in=candidate_pks)
    for d in dsos:
        (az, alt, secz) = d.alt_az(loc, utdt)
        d.azimuth = az
        d.altitude = alt
        d.airmass = secz

    return dict(utdt=utdt, dsos=dsos, location=loc)

def assemble_gear_list(request):
    out = ""
    for g in 'NBSMI':
        name = f"gear{g}"
        out += request.GET.get(name, '')
    return out if len(out) > 0 else None