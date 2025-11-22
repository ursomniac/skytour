from ..apps.stars.models import VariableStar, VariableStarTypeOriginal

def get_type_codes():
    return list(VariableStarTypeOriginal.objects.all().values_list('code', flat=True))

def run_type_test():
    code_list = get_type_codes()
    vv = VariableStar.objects.all()
    bad = {}
    for v in vv:
        types = v.get_all_original_types()
        for type in types:
            if type not in code_list:
                if type not in bad.keys():
                    bad[type] = 1
                else:
                    bad[type] += 1
                print(f"{v.name:<14s}: {v.type_original:<12s} Code {type} not found")
    return bad