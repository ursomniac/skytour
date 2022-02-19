
def serialize_astrometric(target):
    # Equatorial Coordinates
    xra, xdec, xdist = target.radec()
    # Ecliptic Coordinates
    xlat, xlong, _ = target.ecliptic_latlon()

    return dict(
        equ = dict (
            ra = xra.hours,
            dec = xdec.degrees,
            distance = xdist.au
        ),
        ecl = dict (
            latitude = xlat.degrees,
            longitude = xlong.degrees,
        )
    )