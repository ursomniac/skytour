import math

def get_metadata(star):
    md = star.metadata.metadata
    if type(md) == list:
        return md[0], 'list'
    return md, 'dict'

def get_value(d, key, x):
    if key in d.keys():
        return (d[key], 'S') # value comes from Simbad
    return (x, 'B') # value comes from BSC
    
def get_values(star):
    md, objtype = get_metadata(star)
    v = md['values']
    d = {}
    d['objtype'] = objtype
    # Coordinates = skip

    # Magnitudes
    d['magnitude'] = get_value(v, 'magnitude', star.magnitude)

    # Colors
    b_v = get_value(v, 'B-V', star.b_v)
    u_b = get_value(v, 'U-B', star.u_b)
    r_i = get_value(v, 'R-I', star.r_i)
    d['colors'] = dict(b_v=b_v, u_b=u_b, r_i=r_i )

    # Spectral Type
    d['spectral_type'] = get_value(v, 'spectral_type', star.spectral_type)

    # Radial Velocity
    star_rv = dict(value=star.radial_velocity, units='km/s', error=None, flag=star.rv_flag_str)
    zrv = get_value(v, 'radial_velocity', star_rv) # tuple
    vv = zrv[0]
    zrvstr = f"{vv['value']:.2f}"
    zrvstr += '' if not vv['error'] else f" ± {vv['error']:.2f}"
    zrvstr += f" {vv['units']}"
    zrv[0]['shown'] = zrvstr
    d['radial_velocity'] = zrv

    # Proper Motion
    star_pm = dict(
         ra =  dict(value=star.pm_ra,  units='\"/yr'),
         dec = dict(value=star.pm_dec, units='\"/yr'),
         error = None
    )
    zpm = get_value(v, 'proper_motion', star_pm)
    if zpm[1] == 'S':
        vra = zpm[0]['ra']['value']
        vdec = zpm[0]['dec']['value']
        total = math.sqrt(vra**2 + vdec**2)
        zpm[0]['total'] = {'value': total, 'units': zpm[0]['ra']['units']}
    else:
        zpm[0]['total'] = {'value': star.total_proper_motion, 'units': '\"/yr'}
    d['proper_motion'] = zpm

    # Distance
    star_plx = dict(
        value = star.parallax, 
        error=None, units='\"', 
        flag=star.parallax_flag_str,
        shown = f"{star.parallax}\""
    )
    zplx = get_value(v, 'parallax', star_plx)
    if zplx[1] == 'S':
        splx = f"{zplx[0]['value']:.2f}"
        splx += '' if not zplx[0]['error'] else f" ± {zplx[0]['error']:.2f}"
        splx += f" {zplx[0]['units']}"
        zplx[0]['shown'] = splx
        d['parallax'] = zplx

        if v['distance']:
            # parsecs
            zpc = v['distance']['pc']
            spc = f"{zpc['value']:.2f}"
            spc += '' if not zpc['error'] else f" ± {zpc['error']:.2f}"
            #spc += f" pc"
            v['distance']['pc']['shown'] = spc
            # light years
            zly = v['distance']['ly']
            sly = f"{zly['value']:.2f}"
            sly += '' if not zly['error'] else f" ± {zly['error']:.2f}"
            #sly += ' ly'
            v['distance']['ly']['shown'] = sly
        else:
            d['distance'] = None
        d['distance'] = v['distance']
    else:
        d['parallax'] = zplx
        pcs = '' if not star.distance_pc else f"{star.distance_pc:.2f} pc"
        lys = '' if not star.distance else f"{star.distance:.2f} ly"
        d['distance'] = dict(
            pc = {'value': star.distance_pc, 'error': None, 'shown': pcs },
            ly = {'value': star.distance, 'error': None, 'shown': lys }
        )
    # Aliases
    d['simbad_aliases'] = md['aliases']
    return d

