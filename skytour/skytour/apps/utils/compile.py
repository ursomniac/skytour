from .format import to_sex

def observe_to_values(obs):
    """
    Take the object from e.g., earth.at(t).observe(moon)
    and create a dict of all the values and formatted strings.
    """
    (xra, xdec, distance) = obs.radec()
    (elat, elon, distance) = obs.ecliptic_latlon()
    (glat, glon, distance) = obs.galactic_latlon()

    d = {
        'ra': xra.hours.item(),
        #'ra_angle': xra,
        'ra_str': to_sex(xra.hours.item(), format='hours'),
        'dec': xdec.degrees.item(),
        #'dec_angle': xdec,
        'dec_str': to_sex(xdec.degrees.item(), format='degrees'),
        'distance': {
            'au': distance.au.item(),
            'km': distance.km.item(),
            'mi': distance.km.item() / 1.609,
            'light_time': to_sex(distance.light_seconds()/3600., format='hours')
        },
        'ecliptic': {
            'longitude': elon.degrees.item(),
            #'lon_angle': elon,
            'lon_str': to_sex(elon.degrees.item(), format='degrees'),
            'latitude': elat.degrees.item(),
            #'lat_angle': elat,
            'lat_str': to_sex(elat.degrees.item(), format='degrees'),
        },
        'galactic': {
            'longitude': glon.degrees.item(),
            #'lon_angle': glon,
            'lon_str': to_sex(glon.degrees.item(), format='degrees'),
            'latitude': glat.degrees.item(),
            #'lat_angle': glat,
            'lat_str': to_sex(glat.degrees.item(), format='degrees'),
        }
    }
    return d
    