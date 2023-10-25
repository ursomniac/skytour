from .models import DSO, DSOAlias, DSOInField

def search_dso_name(cat, id):
    target = None
    primary = DSO.objects.filter(catalog__abbreviation__iexact=cat, id_in_catalog__iexact=id)
    if primary.count() == 1:
        return primary.first()
    aliases = DSOAlias.objects.filter(catalog__abbreviation__iexact=cat, id_in_catalog__iexact=id)
    if aliases.count() == 1:
        return aliases.first().object
    field_objects = DSOInField.objects.filter(catalog__abbreviation__iexact=cat, id_in_catalog__iexact=id)
    if field_objects.count() == 1:
        return field_objects.first().parent_dso
    return None