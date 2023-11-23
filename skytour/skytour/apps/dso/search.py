import re
from .models import DSO, DSOAlias, DSOInField


def find_cat_id_in_string(string):
    words = string.split(' ') if string[:4] != 'sh2-' else string.split('-')
    if len(words) == 2:
        if words[1].isnumeric():
            return words, None
    if len(words) >= 2: # This is a name
        return None, string
    if len(words) == 1: # This might need to be parsed...
        first_number = re.search(r"\d", string)
        if first_number:
            cat = string[:first_number.start()]
            id_in_cat = string[first_number.start():]
            return [cat, id_in_cat], None
        else:
            return None, string

def search_dso_name(words, name):
    target = None
    if words is not None:
        cat, id = words
        primary = DSO.objects.filter(catalog__abbreviation__iexact=cat, id_in_catalog__iexact=id)
        if primary.count() > 0:
            return primary.first()
        aliases = DSOAlias.objects.filter(catalog__abbreviation__iexact=cat, id_in_catalog__iexact=id)
        if aliases.count() > 0:
            return aliases.first().object
        field_objects = DSOInField.objects.filter(catalog__abbreviation__iexact=cat, id_in_catalog__iexact=id)
        if field_objects.count() > 0:
            return field_objects.first().parent_dso
    else:
        names = DSO.objects.filter(nickname__icontains=name)
        if names.count() > 0:
            return names.first()
        field_names = DSOInField.objects.filter(nickname__icontains=name)
        if field_names.count() > 0:
            return field_names.first().parent_dso
    return None