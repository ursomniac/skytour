from skytour.apps.dso.models import DSO

def make_shell_script():
    lines = []
    cmd = "python manage.py create_dso_finder_chart --dso_list "
    all_ids = DSO.objects.order_by('pk').values_list('pk')
    total = all_ids.count()
    id_list = [x[0] for x in all_ids]

    while len(id_list) > 0:
        next = [str(i) for i in id_list[:20]]
        s = ' '.join(next)
        lines.append(f"{cmd}{s}")
        id_list = id_list[20:]
    return lines
