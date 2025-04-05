from .finder import plot_dso_list
from .geo import get_circle_center
from .helpers import get_star_mag_limit
from .models import DSO, DSOList

def get_active_dsolist_objects(mode='I', priority=4):
    active_lists = DSOList.objects.filter(active_observing_list=True)
    list_pks = active_lists.values_list('pk', flat=True)
    all_dsos = DSO.objects.filter(dsolist__pk__in=list_pks).distinct()
    filter_dsos = []
    for dso in all_dsos:
        modes = dso.dsoobservingmode_set.filter(mode=mode, priority__gte=priority)
        if modes.count() > 0:
            filter_dsos.append(dso)
    return filter_dsos

def get_dso_list_map(dso_list, priority=4, mode='I'):
    map = None
    center_ra, center_dec, max_dist = get_circle_center(dso_list)
    #print(f"RA: {center_ra} DEC: {center_dec}  MD: {max_dist}")
    if (max_dist is None or max_dist < 0.001)  and center_ra is not None:
        max_dist = 5.
    if max_dist is not None and max_dist > 0.:
        fov = max_dist * 1.2

        star_mag_limit = get_star_mag_limit(max_dist)

        map = plot_dso_list(
            center_ra, 
            center_dec,
            dso_list,
            fov=fov,
            star_mag_limit = star_mag_limit,
            reversed = False,
            label_size='small',
            symbol_size=60,
            title = f"Active DSOs: Mode { mode }, Priority ≥ { priority }"
        )
    return map