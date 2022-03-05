import hmac


SEX_FORMAT = {
    'hours': "{}{:02d}h {:02d}m {:06.3f}s",
    'hms': "{}{:02d}:{:02d}:{:02d}",
    "hmsf": "{}{:02d}:{:02d}:{:06.3f}",
    'degrees': "{:1s}{:3d}° {:02d}\' {:06.3f}\"", # SHOULD be -360 to 360
    'deg_text': "{:1s}{:3d}d {:02d}m {:06.3f}s",
    "ra": "{}{:02d}h{:02d}m{:06.3f}s", # ra SHOULD be positive, < 24
    "dec": "{:1s}{:02d}°{:02d}\'{:06.3f}\"" # dec SHOULD be -90 to 90.
}

def to_sex(value, format='hours'):
    """
    Turn a floating point value (hours or degrees), and return 
    a text representation e.g,.  12h 30m 34.23s
    """
    x = abs(value)
    if format in ["hours", "hms", "hmsf", "ra"]:
        sign = '' if value > 0 else '-'
    else:
        sign = '+' if value > 0 else '-'
    h = int(x)
    x -= h
    x *= 60.
    m = int(x)
    s = (x-m) * 60
    if format == 'hms':
        s = int(s)

    return SEX_FORMAT[format].format(sign, h, m, s)

def to_hm(value):
    x = abs(value)
    h = int(x)
    x -= h
    x *= 60.
    m = x
    return f'{h:02d}h {m:04.1f}m'

def to_dm(value):
    x = abs(value)
    sign = '+' if value > 0 else '-'
    d = int(x)
    x -= d
    x *= 60.
    m = int(x)
    return f"{sign}{d:02d}° {m:02d}\'"

def to_time(value):
    x = abs(value)
    l = []
    h = int(x)
    if h != 0:
        l.append(f'{h:02d}')
    x -= h
    x *= 60.
    m = int(x)
    l.append(f'{m:02d}')
    x -= m
    x *= 60.
    l.append(f'{x:04.1f}')
    return ':'.join(l)
