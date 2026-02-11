import datetime
from django import template
from django.utils.html import mark_safe
from skytour.apps.dso.vocabs import PRIORITY_COLORS
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
        w = n + 3 if n != 0 else 2
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
        w = n + 3 if n != 0 else 2
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

@register.filter(name="show_property_source")
def show_property_source(code):
    d = {
        'S': 'Simbad',
        'H': 'HyperLeda',
        'L': 'HyperLeda'
    }
    return d[code] if code in d.keys() else ''

@register.filter(name='mode_priority_span')
def mode_priority_span(d, mode='S'):
    print("D: ",d)
    try:
        VALS = {'None': 0, 'Lowest': 0, 'Low': 1, 'Medium': 2, 'High': 3, 'Highest': 4}
        pri = 'None'
        if mode in d.keys():
            pri = d[mode]

        color = PRIORITY_COLORS[pri]
        val = VALS[pri]
        out = f'<span style="color: {color}">{val} - {pri}</span>'
    except:
        out = 'Unknown'
    return mark_safe(out)

@register.filter(name='modulo')
def modulo(num, val):
    return num % val

@register.filter(name='month_day')
def month_day(yearless_date):
    """
    Given (int) month and day (but not year), return text values.
    2025 is a "fudge year" because it doesn't have to be known.
    """
    t = datetime.date(2025, yearless_date.month, yearless_date.day)
    return t.strftime("%b %d")

@register.filter(name='month_day_string')
def month_day_string(yearless_date):
    """
    given (int) month and (int) day return e.g,. 0802 making dates suitable
    for sorting even if the shown values are text (so June < July, and Dec > Nov).
    """
    return f"{yearless_date.month:02d}{yearless_date.day:02d}"

@register.filter(name='sortable_angle')
def sortable_angle(value, offset=90):
    """
    This gets around the problem of sortable columns of angles being formatted in
    way that doesn't understand it needs to sort numerically (i.e., -90° to +90°, etc.)
    So it offsets the value by an offset such that all of the values are positive, then
    formats that with leading zeros so that sorting on a list of values happens correctly.

    In the template, just hide the calculated value (display: none).
    """
    try:
        v = float(value) + offset
        return f"A{abs(v):08.4f}"
    except:
        return value
    
@register.filter(name='sortable_float')
def sortable_angle(value, format="05.2f"):
    try:
        v = float(value)
        return f"{v:{format}}"
    except:
        return value

@register.filter(name='add_two')
def add_two(value, arg):
    try:
        return float(value) + float(arg)
    except:
        return None