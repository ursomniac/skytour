from math import sin, cos, asin, acos, radians, degrees, atan2, sqrt, pow

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
    if n < 1: 
        return None, None, None
    elif n == 1:
        return dso_list[0].ra, dso_list[0].dec, None
    min_cos_d = 1.
    dd1 = None
    dd2 = None
    min_ra = None
    max_ra = None
    min_dec = None
    max_dec = None

    # the matrix of disances only has to go half-way, e.g., d(1, 2) = d(2, 1)
    for i in list(range(n)):
        dso1 = dso_list[i]
        ra1 = radians(dso1.ra * 15.)
        dec1 = radians(dso1.dec)

        min_dec = dso1.dec if min_dec is None or dso1.dec < min_dec else min_dec
        max_dec = dso1.dec if max_dec is None or dso1.dec > max_dec else max_dec
        min_ra  = dso1.ra  if min_ra  is None or dso1.ra  < min_ra  else min_ra
        max_ra  = dso1.ra  if max_ra  is None or dso1.ra  > max_ra  else max_ra

        if debug:
            print(f"DSO: {dso1} RA: {dso1.ra:.3f} Dec: {dso1.dec:.3f} RA: {min_ra:.3f} {max_ra:.3f} DEC: {min_dec:.3f} to {max_dec:.3f} ")
        
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

    if dd1 is None or dd2 is None:
        return None, None, None

    # Get max distance between DSOs - this defines the radius
    sep = degrees(acos(min_cos_d))

    if debug:
        print(f"DSO1: {dd1} RA: {dd1.ra:6.3f} DEC: {dd1.dec:7.3f}")
        print(f"DSO2: {dd2} RA: {dd2.ra:6.3f} DEC: {dd2.dec:7.3f}")
        print(f"\tmin cos d = {min_cos_d:.3f}: d = {sep:.3f}")
        print(f"RA range: {min_ra:.3f} to {max_ra:.3f}")
        print(f"Dec. range: {min_dec:.3f} to {max_dec:.3f}")

    # Get the mid RA and Dec
    mid_dec = (min_dec + max_dec) / 2.

    delta_ra = abs(max_ra - min_ra)
    if debug:
        print(f"Delta RA: {delta_ra:.3f}")
    if delta_ra > 12.:
        total_ra = max_ra + min_ra + 24.
        mid_ra = (total_ra / 2.) % 24.
    else:
        mid_ra = (min_ra + max_ra) / 2.

    if debug:
        print(f"Mid RA: {mid_ra:.3f} ")
        print(f"Mid Dec: {mid_dec:.3f}")
    
    return mid_ra, mid_dec, sep

"""
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
        dmin = None
        dmax = None
        min_xyz = None
        max_xyz = None

        for d in dso_list:
            x, y, z = get_xyz(d.ra, d.dec)
            xx.append(x)
            yy.append(y)
            zz.append(z)

            #print(f"DSO: {d} RA: {d.ra:.3f} X: {x:.3f}  Y: {y:.3f} Z: {z:.3f} ")
            if x == min(xx):
                dmin = d
                min_xyz = (x, y, z)
                #print(f"\tnew min X: {x}")
            if x == max(xx):
                dmax = d
                #print(f"\tnew max X: {x}")
                max_xyz = (x, y, z)

        cx = (min(xx) + max(xx)) / 2.
        cy = (min(yy) + max(yy)) / 2.
        cz = (min(zz) + max(zz)) / 2.
        ld = sqrt(cx*cx + cy*cy + cz*cz)

        print(f"X: {cx:.3f} = {min(xx):.3f} to {max(xx):.3f}")
        print(f"Y: {cy:.3f} = {min(yy):.3f} to {max(yy):.3f}")
        print(f"Z: {cz:.3f} = {min(zz):.3f} to {max(zz):.3f}")

        longitude = atan2(cy, cx)
        latitude = asin(cz / ld)

        cra = (degrees(longitude) / 15.) % 24.
        print(f"CRA: {cra:.3f}")
        #cra += 12. if (max_ra-min_ra) > 12. else 0.
        cra += 12. if min(xx) < 0. and max(xx) > 0. else 0.
        cra %= 24.
        cdec = degrees(latitude)
        
        print(f"Center: {cra:.3f} {cdec:.3f}")

        # Min X coordinates
        min_ra = degrees(atan2(min_xyz[1], min_xyz[0])) / 15. % 24.
        max_ra = degrees(atan2(max_xyz[1], max_xyz[0])) / 15. % 24.
        min_ld = sqrt(pow(min_xyz[0], 2.) + pow(min_xyz[1], 2.) + pow(min_xyz[2], 2.))
        max_ld = sqrt(pow(max_xyz[0], 2.) + pow(max_xyz[1], 2.) + pow(max_xyz[2], 2.))
        min_dec = degrees(asin(min_xyz[2] / min_ld))
        max_dec = degrees(asin(max_xyz[2] / max_ld))

        print(f"MIN X Coords: {min_ra:.3f}, {min_dec:.3f} {dmin}, {dmin.ra}, {dmin.dec}")
        print(f"MAX X Coords: {max_ra:.3f}, {max_dec:.3f} {dmax}, {dmax.ra} {dmax.dec}")

        if debug:
            print(f"Center RA: {cra:6.3f}")
            print(f"Center Dec: {cdec:7.3f}")
            print(f"Radius: {sep/2.:7.3f}°")
        return cra, cdec, sep/2.
"""