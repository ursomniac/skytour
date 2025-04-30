import re
from .models import DSO, DSOAlias, DSOInField, DSOInFieldAlias


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

def search_dso_name(words, name, debug=False):
    if words is not None:
        cat, id = words
        # Easy lookup
        primary = DSO.objects.filter(catalog__abbreviation__iexact=cat, id_in_catalog__iexact=id)
        if debug:
            print(f"{cat}, {id}: primary found {primary}")
        if primary.count() > 0:
            return primary.first()

        # Maybe it's an alias
        aliases = DSOAlias.objects.filter(catalog__abbreviation__iexact=cat, id_in_catalog__iexact=id)
        if debug:
            print(f"{cat}, {id}: aliases found {aliases}")
        if aliases.count() > 0:
            return aliases.first().object
        
        # Maybe it's a DSO in the field of another DSO
        field_objects = DSOInField.objects.filter(catalog__abbreviation__iexact=cat, id_in_catalog__iexact=id)
        if debug:
            print(f"{cat}, {id}: in field found {field_objects}")
        if field_objects.count() > 0:
            return field_objects.first().parent_dso
        
        # Maybe it's a DSOInField alias
        field_aliases = DSOInFieldAlias.objects.filter(
            catalog__abbreviation__iexact=cat,
            id_in_catalog__iexact=id
        )
        if field_aliases.count() > 0:
            return field_aliases.first().object.parent_dso
        
        # Maybe it's a map label
        idstr = ' '.join(words)
        map_name_objects = DSO.objects.filter(map_label__iexact=idstr)
        if debug:
            print(f"{idstr}: map label found {map_name_objects}")
        if map_name_objects.count() > 0:
            return map_name_objects.first()
        
        # maybe it's a nickname
        nickname_objects = DSO.objects.filter(nickname__istartswith=idstr)
        if nickname_objects.count() > 0:
            return nickname_objects.first()
        
        # Maybe it's in the other catalog
        other_objects = DSO.objects.filter(catalog__abbreviation='OTHER', id_in_catalog__iexact=idstr)
        if debug:
            print(f"{idstr}: other objects found {other_objects}")
        if other_objects.count() > 0:
            return other_objects.first()
        
    # TODO V2.x: come up with better logic for this
    # if you send one word as a name then it can get confused...
    else:
        names = DSO.objects.filter(nickname__icontains=name)
        if debug:
            print(f"name {name} found {names}")
        if names.count() == 1:
            return names.first()
        elif names.count() > 1:
            names = DSO.objects.filter(nickname__istartswith=name)
            if names.count() >= 1:
                return names.first()
        
        field_names = DSOInField.objects.filter(nickname__icontains=name)
        if debug:
            print(f"name {name}: field names found {field_names}")
        if field_names.count() > 0:
            return field_names.first().parent_dso
        
        map_name_objects = DSO.objects.filter(map_label__iexact=name)
        if debug:
            print(f"name {name}: map names found {map_name_objects}")
        if map_name_objects.count() > 0:
            return map_name_objects.first()
    return None