def get_filter_list(request):
    filters = []
    filter_names = ['seen', 'important', 'unseen', 'available', 'imaged', 'unimaged']
    for f in filter_names:
        if request.GET.get(f, False):
            filters.append(f)
    return filters


def filter_dso_test(dso, filters):
    if filters is None:
        return dso
    if 'seen' in filters and dso.observations.count() == 0:
        return None
    if 'important' in filters and dso.priority not in ['High', 'Highest']:
        return None
    if 'unseen' in filters and dso.observations.count() != 0:
        return None
    if 'available' in filters and dso.priority == 'None':
        return None
    if 'imaged' in filters and dso.num_library_images == 0:
        return None
    if 'unimaged' in filters and dso.num_library_images != 0:
        return None
    return dso