import datetime as dt, pytz
from ..dso.models import DSO
from ..observe.models import ObservingLocation

def parse_imaged_value(v):
    if v == 'All':
        return None
    return v == 'Yes'

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
    
def is_in_window(location_id, az, alt, min_alt=10.):
    if location_id is None:
        return True
    if location_id != 1:
        return alt >= min_alt
    
    # check against home
    if alt > 70.:
        return True
    if alt < min_alt:
        return False
    
    if az < 120.:
        return False
    if az >= 120. and az <= 160. and alt < 30.:
        return False
    if az >= 160. and az <= 210. and alt < 48.:
        return False
    if az >= 210. and az < 230.:
        if alt >= 15. and alt <= 30.:
            return True
        elif alt >= 30. and alt <= 50.:
            return False
    elif az > 230.:
        return False
    return True
    
def find_objects_at_home(
        utdt = None, # set to now if none 
        offset_hours = 0., 
        imaged = False,
        min_priority = 0,
        #
        location_id = 1,
        min_dec = -20.,
        min_alt = 30.
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
        if imaged == True and d.library_image is None:
            continue
        elif imaged == False and d.library_image is not None and d.reimage == False:
            # TODO: What about re-imaging?
            continue

        (az, alt, _) = d.alt_az(loc, utdt)
        if is_in_window(location_id, az, alt):
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
        imaged = False,
        min_priority = 0,
        #
        location = None,
        min_dec = -30.,
        min_alt = 30.,
    ):
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
        if imaged == True and d.library_image is None:
            continue
        elif imaged == False and d.library_image is not None and d.reimage == False:
            continue

        (az, alt, _) = d.alt_az(loc, utdt)
        if is_in_window(loc.id, az, alt):
            candidate_pks.append(d.pk)

    dsos = DSO.objects.filter(pk__in=candidate_pks)
    for d in dsos:
        (az, alt, secz) = d.alt_az(loc, utdt)
        d.azimuth = az
        d.altitude = alt
        d.airmass = secz

    return dict(utdt=utdt, dsos=dsos, location=loc)
