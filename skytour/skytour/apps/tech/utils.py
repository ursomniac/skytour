import math

def get_sensor_field_of_view(focal_length, px, py, psize, units='arcmin'):
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

def get_sensor_pixel_resolution(focal_length, psize, units='arcsec'):
    r2s = 3437.7462 * 60.  # radians to arcseconds
    res = psize/1000. * r2s / focal_length # arcseconds
    if units == 'degrees':
        res /= 3600.
    elif units == 'arcmin':
        res /= 60.
    return res

def get_sensor_megapixels(x, y, base10=True):
    denom = 1.e6 if base10 else 1024*1024
    return x * y / denom

def get_telescope_f_ratio(focal_length, aperture):
    return focal_length/aperture

def get_telescope_limiting_magnitude(aperture):
    # old: 3.7 + 2.5 * math.log10(aperture)
    return 9.5 + 5.0 * math.log10(aperture)

def get_telescope_raleigh_limit(aperture, units="arcsec"):
    theta = 138. / aperture
    if units == 'degrees':
        theta /= 3600.
    elif units == 'arcmin':
        theta /= 60.
    return theta

def get_telescope_dawes_limit(aperture, units="arcsec"):
    theta = 116. / aperture
    if units == 'degrees':
        theta /= 3600.
    elif units == 'arcmin':
        theta /= 60.
    return theta

def get_eyepiece_magnification(
        telescope_focal_length,
        eyepiece_focal_length,
        normalize = True
    ):
    x = telescope_focal_length / eyepiece_focal_length
    if normalize:
        m = int(10.*(x + 0.05))/10.
        return m
    return x

def get_eyepiece_field_of_view(apparent_fov, magnification, units="degrees"):
    x = apparent_fov / magnification
    if units == 'arcmin':
        x *= 60.
    elif units == 'arcsec':
        x *= 3600.
    return x
