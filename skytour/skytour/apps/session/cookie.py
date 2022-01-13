def get_session_cookie(request):
    try:
        cookie = request.session['session']
    except Exception:
        cookie = None
    return cookie