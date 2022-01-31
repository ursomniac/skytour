from django import template
register = template.Library()

@register.filter(name='dict_value')
def dict_value(value, arg):
    return value.get(arg, None)

@register.filter(name='to_hms')
def to_hms(d, n=3):
    try:
        x = d % 24.
        h = int(x)
        x = (x - h) * 60.
        m = int(x)
        s = (x - m) * 60.
        d = n + 3
        return f"{h:02d}h {m:02d}m {s:0{d}.{n}f}s"
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


@register.filter(name='to_dms')
def to_dms(d, n=3):
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
    letters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    return letters[i % 26]

@register.filter(name="modulus")
def modulus(x, y):
    return x % y