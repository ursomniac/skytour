from skytour.apps.dso.models import DSO

"""
V2: KEEP for test
Test to make sure that DSOInField are - in fact - IN the field
(sometimes things get entered incorrectly...)
"""
def check_dso(max_dist=30.):
    dsos = DSO.models.order_by('pk')
    for dso in dsos:
        if dso.dsos_in_field_count < 1:
            continue
        fdsos = dso.dsos_infield_set.all()
        for f in fdsos:
            if f.primary_distance > max_dist:
                print(f"{dso}: {f} at {f.primary_distance:.2f}")

if __name__=='__main__':
    check_dso()