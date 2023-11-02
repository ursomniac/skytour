import datetime
from django import template
#from skytour.apps.utils.format import float2ang
register = template.Library()

@register.filter(name='dict_value')
def dict_value(value, arg):
    """
    Return a dictionary's value given the key.
    Usage:  {{ foo|dict_value:key }}
    """
    return value.get(arg, None)

@register.filter(name='to_hms')
def to_hms(d, n=3):
    """
    Given a floating hour value (e.g., right ascension)
    return a string in the format ±00h 00m 00.[000]s where
    the precision on the seconds value defaults to 3 but 
    can be sent via the call.
    Usage: {{ foo|to_hms }} or {{ foo|to_hms:1 }}
    """
    try:
        sign = '-' if d < 0. else ''
        x = abs(d) % 24
        h = int(x)
        x = (x - h) * 60.
        m = int(x)
        s = (x - m) * 60.
        d = n + 3
        return f"{sign}{h:02d}h {m:02d}m {s:0{d}.{n}f}s"
    except:
        return None

@register.filter(name='dt_hms')
def dt_hms(d, n=3):
    """
    Allow negative times
    """
    try:
        sign = '+' if d > 0. else '-'
        x = abs(d)
        h = int(x)
        x = (x-h) * 60.
        m = int(x)
        s = (x-m) * 60.
        w = n + 3
        return f"{sign}{h:02d}h {m:02d}m {s:0{w}.{n}f}s"
    except:
        return None

@register.filter(name='to_hm')
def to_hm(d, n=2):
    """
    Mostly the same as above, except seconds are omitted.
    The precision of the minutes value can be set as a parameter.
    Usage:  {{ foo|to_hm }} or {{ foo|to_hm:1 }}
    """
    try:
        x = abs(d)
        h = int(x)
        m = (x-h) * 60.
        if m >= 60.0:
            m -= 60.
            h += 1
        w = n + 3
        return f"{h:02d}h {m:0{w}.{n}f}m"
    except:
        return None

@register.filter(name='to_dm')
def to_dm(d, n=2):
    """
    Same as above except negative values are allowed.
    """
    try:
        sign = '+' if d > 0. else '-'
        x = abs(d)
        h = int(x)
        m = (x-h) * 60.
        w = n + 3
        return f"{sign}{h:02d}° {m:0{w}.{n}f}\'"
    except:
        return None


@register.filter(name='to_dms')
def to_dms(d, n=3):
    """
    Similar to above, except the string returned is an angle (degrees, minutes, seconds).
    Usage: {{ foo|to_dms }} or {{ foo|to_dms:2 }}
    """
    try:
        x = abs(d)
        h = int(x)
        x = (x - h) * 60.
        m = int(x)
        s = (x - m) * 60.
        sign = '-' if d < 0 else '+'
        w = n + 3
        return f"{sign}{h:3d}° {m:02d}\' {s:{w}.{n}f}\""
    except:
        return None

@register.filter(name='to_dhms')
def to_dhms(x):
    """
    Similar to the above except the floating value is in decimal days.
    So the output string is e.g., 3d 06h 12m 18.33s
    """
    try:
        d = int(x)
        hms = (x - d) * 24.
        h = int(hms)
        hms = (hms - h) * 60.
        m = int(hms)
        s = (hms - m) * 60.
        return "{}d {:02d}h {:02d}m {:0.2f}s".format(d, h, m, s)
    except:
        return None

@register.filter(name='letter_index')
def letter_index(i):
    """
    Returns a cycle of letters (will repeat if the index is >25).
    Zero indexed (i.e., 0 = A, 1 = B, etc.).
    This is used on Skymap to generate comet labels.

    Usage: {{ foo|letter_index:8 }} returns 'G'
    """
    letters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    return letters[i % 26]

@register.filter(name="modulus")
def modulus(x, y):
    """
    Return x mod y.
    Usage: {{ foo|modulus:4 }}
    """
    return x % y

@register.filter(name="get_datetime")
def get_datetime(x):
    """
    X is a string, convert to datetime.
    """
    return datetime.datetime.fromisoformat(x)

@register.filter(name='get_local_time')
def get_local_time(x):
    """
    X is a isoformat string with time zone
    """
    dt = datetime.datetime.fromisoformat(x)
    return dt.strftime("%b %-d, %Y %-I:%M %p %z")