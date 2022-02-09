
def get_limiting_magnitude(bortle):
    if bortle is None:
        return None
    vrange = [
        None, '≥ 7.5', '7.0 - 7.5', '6.5 - 7.0',
        '6.0 - 6.5', '5.5 - 6.0', '5.0 - 5.5',
        '4.5 - 5.0', '4.0 - 4.5', '< 4.0'
    ]
    return vrange[bortle]