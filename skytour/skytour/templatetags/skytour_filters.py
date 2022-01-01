from django import template
register = template.Library()

@register.filter(name='dict_value')
def dict_value(value, arg):
    return value.get(arg, None)

@register.filter(name='to_hms')
def to_hms(d):
    try:
        x = d % 24.
        h = int(x)
        x = (x - h) * 60.
        m = int(x)
        s = (x - m) * 60.
        return "{:02d}h {:02d}m {:6.3f}s".format(h, m, s)
    except:
        return None

@register.filter(name='to_dms')
def to_dms(d):
    try:
        x = abs(d)
        h = int(x)
        x = (x - h) * 60.
        m = int(x)
        s = (x - m) * 60.
        sign = '-' if d < 0 else '+'
        return "{}{:3d}° {:02d}\' {:6.3f}\"".format(sign, h, m, s)
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