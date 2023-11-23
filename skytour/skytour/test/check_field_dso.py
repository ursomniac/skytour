from skytour.apps.dso.models import DSO

def check_dso():
    dsos = DSO.models.order_by('pk')
    for dso in dsos:
        if dso.dsos_in_field_count < 1:
            continue
        fdsos = dso.dsos_infield_set.all()
        for f in fdsos:
            if f.primary_distance > 30.:
                print(f"{dso}: {f} at {f.primary_distance:.2f}")

if __name__=='__main__':
    check_dso()