import datetime as dt, pytz
from ..dso.models import DSO
from ..observe.models import ObservingLocation

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
    utdt = dt.datetime.now().replace(tzinfo=pytz.utc) if utdt is None else utdt
    utdt += dt.timedelta(hours=offset_hours)
    # 2. get latitude/longitude
    loc =  ObservingLocation.objects.get(pk=location_id)
    # 3. get DSOs
    dsos = DSO.objects.filter(dec__gte=min_dec)

    #candidates = []
    candidate_pks = []
    for d in dsos:

        # Filter based on existing images
        if d.imaging_checklist_priority < min_priority:
            continue
        if imaged == True and d.library_image is None:
            continue
        elif imaged == False and d.library_image is not None:
            continue

        (az, alt, _) = d.alt_az(loc, utdt)
        if alt > 70.: # keep!
            #candidates.append(d)
            candidate_pks.append(d.pk)
        elif alt < min_alt: 
            continue
        elif az < 120.:
            continue
        elif az > 230.: 
            continue
        elif az > 160.: # Kim's house
            skim = 30. + 20. * (az - 160.) / 70.
            if alt < skim:
                continue
            else:
                candidate_pks.append(d.pk)
        else: # in the window!
            candidate_pks.append(d.pk)
    # Return as a queryset 
    # Ideally this should ALSO contain alt/az!
    dsos = DSO.objects.filter(pk__in=candidate_pks)
    for d in dsos:
        (az, alt, secz) = d.alt_az(loc, utdt)
        d.azimuth = az
        d.altitude = alt
        d.airmass = secz
    return dict(utdt=utdt, dsos=dsos)

