from .models import DSOList

def create_dso_list_from_queryset(dsos, name='Default Name', description=None):
    x = DSOList()
    x.name = name
    x.description = description
    x.save()
    x.dso.add(*dsos)
    x.save()
    return x

