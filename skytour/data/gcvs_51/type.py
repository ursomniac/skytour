import re

def split_types(x):
    if x is not None:
        return re.split(r"[+|/]", x.replace(':',''))
    return []

def count_types(vv):
    old = {}
    new = {}
    for v in vv:
        o = v.type_original
        n = v.type_revised
        for t in split_types(o):
            if t in old.keys():
                old[t] += 1
            else:
                old[t] = 1
        for t in split_types(n):
            if t in new.keys():
                new[t] += 1
            else:
                new[t] = 1
    return old, new