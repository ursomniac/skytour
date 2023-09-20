from math import sin, cos, acos, radians, degrees, atan2, sqrt

def get_xyz(ra, dec, debug=False):
    xra = radians(ra * 15.)
    xdec = radians(dec)
    x = sin(xdec) * cos(xra)
    y = sin(xdec) * sin(xra)
    z = cos(xdec)
    
    if debug:
        print(f"RA: {ra:.3f} = {ra*15.:.3f}° = {xra:.3f} radians")
        print(f"Dec: {dec:.3f} = {xdec:.3f} radians")
        print(f"X: {x:.3f}  Y: {y:.3f} Z: {z:.3f}")
        print()

    return x, y, z

def get_midpoint(x1, y1, z1, x2, y2, z2, debug=False):
    x = (x1 + x2)/2.
    y = (y1 + y2)/2.
    z = (z1 + z2)/2.

    if debug:
        print(f"X {x:.3f} = {x1:.3f} + {x2:.3f} / 2.")
        print(f"Y {y:.3f} = {y1:.3f} + {y2:.3f} / 2.")
        print(f"Z {z:.3f} = {z1:.3f} + {z2:.3f} / 2.")

    ld = sqrt(x*x + y*y + z*z)
    if debug:
        print(f"LD: = {ld:.3f} = sqrt {x*x:.3f} + {y*y:.3f} + {z*z:.3f}")

    longitude = atan2(y, x)
    latitude = acos(z / ld)

    ra = (degrees(longitude) / 15.) % 24.
    dec = degrees(latitude)

    if debug:
        #print(f"X: {x:.3f}  Y: {y:.3f} Z: {z:.3f}")
        #print(f"LD: {ld:.4f}")
        print(f"Long: {longitude:.3f} radians = {degrees(longitude):.3f}°")
        print(f"Lat: {latitude:.3f} radians = {degrees(latitude):.3f}°")
        print(f"RA: {ra:.3f} Dec: {dec:.3f} ")

    return ra, dec

def get_circle_center(dso_list, strategy='midxyz', debug=False):
    n = len(dso_list)
    min_cos_d = 1.
    dd1 = None
    dd2 = None

    # the matrix of disances only has to go half-way, e.g., d(1, 2) = d(2, 1)
    for i in list(range(n)):
        dso1 = dso_list[i]
        ra1 = radians(dso1.ra * 15.)
        dec1 = radians(dso1.dec)
        for j in list(range(i+1, n)):
            #print(f"I: {i} J: {j}")
            dso2 = dso_list[j]
            ra2 = radians(dso2.ra * 15.)
            dec2 = radians(dso2.dec)

            # Get angular distance between the two points
            cos_d = sin(dec1) * sin(dec2) 
            cos_d += cos(dec1) * cos(dec2) * cos(ra1 - ra2)

            if cos_d < min_cos_d:
                dd1 = dso1
                dd2 = dso2
                min_cos_d = cos_d
    
    sep = degrees(acos(min_cos_d))

    if debug:
        print(f"DSO1: {dd1} RA: {dd1.ra:6.3f} DEC: {dd1.dec:7.3f}")
        print(f"DSO2: {dd2} RA: {dd2.ra:6.3f} DEC: {dd2.dec:7.3f}")
        print(f"\tmin cos d: {min_cos_d}")
        print(f"\td: {sep}°")

    if strategy=='centroid':
        x1, y1, z1 = get_xyz(dd1.ra, dd1.dec, debug=debug)            
        x2, y2, z2 = get_xyz(dd2.ra, dd2.dec, debug=debug)
        cra, cdec = get_midpoint(x1, y1, z1, x2, y2, z2, debug=debug)
    elif strategy=='simple':
        tdd = dd1.ra + dd2.ra
        tdd += 0 if dd1.ra > dd2.ra else 12.
        cra = (tdd / 2.) % 24.
        cdec = (dd1.dec + dd2.dec) / 2.
    elif strategy=='middle':
        min_ra = None
        max_ra = None
        min_dec = None
        max_dec = None
        for d in dso_list:
            min_ra = d.ra if min_ra is None or d.ra < min_ra else min_ra
            max_ra = d.ra if max_ra is None or d.ra > max_ra else max_ra
            min_dec = d.dec if min_dec is None or d.dec < min_dec else min_dec
            max_dec = d.dec if max_dec is None or d.dec > max_dec else max_dec

        if debug:
            print(f"RA {min_ra:.3f} to {max_ra:.3f}")
            print(f"Dec: {min_dec:.3f} to {max_dec:.3f}")

        cra = (min_ra + max_ra) / 2.
        cra += 12. if (max_ra - min_ra) > 12. else 0.
        cra %= 24.
        cdec = (min_dec + max_dec) / 2.
    elif strategy == 'midxyz':
        xx = []
        yy = []
        zz = []
        for d in dso_list:
            x, y, z = get_xyz(d.ra, d.dec)
            xx.append(x)
            yy.append(y)
            zz.append(z)
        cx = (min(xx) + max(xx)) / 2.
        cy = (min(yy) + max(yy)) / 2.
        cz = (min(zz) + max(zz)) / 2.
        ld = sqrt(cx*cx + cy*cy + cz*cz)

        longitude = atan2(cy, cx)
        latitude = acos(cz / ld)

        cra = (degrees(longitude) / 15.) % 24.
        cdec = degrees(latitude)

    else:
        cra = None
        cdec = None

    if debug:
        print(f"Center RA: {cra:6.3f}")
        print(f"Center Dec: {cdec:7.3f}")
        print(f"Radius: {sep/2.:7.3f}°")
    return cra, cdec, sep/2.

