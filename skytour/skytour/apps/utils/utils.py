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
    return dso