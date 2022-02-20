from ..utils.format import to_sex

def serialize_astrometric(target):
    # Equatorial Coordinates
    xra, xdec, xdist = target.radec()
    ra = xra.hours.item()
    dec = xdec.degrees.item()
    light_time = xdist.light_seconds().item() / 3600. # hours
    # Ecliptic Coordinates
    xlat, xlong, _ = target.ecliptic_latlon()
    lat = xlat.degrees.item()
    lon = xlong.degrees.item()

    return dict(
        equ = dict (
            ra = ra, 
            ra_str = to_sex(dec, format='hours'),
            dec = dec,
            dec_str = to_sex(dec, format='degrees')
        ),
        ecl = dict (
            latitude = lat,
            lat_str = to_sex(lat, format='degrees'),
            longitude = lon,
            lon_str = to_sex(lon, format='degrees') 
        ),
        distance = dict (
            au = xdist.au.item(), 
            km = xdist.km.item(),
            mi = xdist.km.item() / 1.609,
            light_time = light_time,
            light_time_str = to_sex(light_time, format='hours')
        )
    )