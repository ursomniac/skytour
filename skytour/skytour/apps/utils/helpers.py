from ..session.cookie import get_cookie

def get_objects_from_cookie(request, cookie_type, constellation):
    cookie = get_cookie(request, cookie_type)
    if cookie is None:
        return None
    objects = []
    if cookie_type == 'planets':
        for k in cookie.keys():
            obj = cookie[k]
            if obj['observe']['constellation']['abbr'].upper() == constellation:
                objects.append(cookie[k])
    else: # Comets and asteroids are in lists
        for obj in cookie:
            if obj['observe']['constellation']['abbr'].upper() == constellation:
                objects.append(obj)
    return objects