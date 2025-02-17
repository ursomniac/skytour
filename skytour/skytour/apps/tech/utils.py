
def get_field_of_view(focal_length, px, py, psize, units='arcmin'):
    r2m = 3437.74620 # 180/pi * 60 == radians to arcminutes
    x = px * psize/1000. / focal_length * r2m
    y = py * psize/1000. / focal_length * r2m
    if units == 'degrees':
        x /= 60.
        y /= 60.
    if units == 'arcsec':
        x *= 60.
        y *= 60.
    return (x, y)

def get_pixel_resolution(focal_length, psize, units='arcsec'):
    r2s = 3437.7462 * 60.  # radians to arcseconds
    res = psize/1000. * r2s / focal_length # arcseconds
    if units == 'degrees':
        res /= 3600.
    elif units == 'arcmin':
        res /= 60.
    return res

def get_megapixels(x, y, base10=True):
    denom = 1.e6 if base10 else 1024*1024
    return x * y / denom