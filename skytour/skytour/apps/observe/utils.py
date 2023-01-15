import pandas as pd
def get_mean_obs_sqm(loc, include_moon=False):

    sessions = loc.observingsession_set.all()
    loc_sqm_list = []
    for session in sessions:
        circumstances = session.observingcircumstances_set.all()
        sqm_list = []
        for circ in circumstances:
            if circ.sqm is None:
                continue
            if circ.moon and not include_moon:
                continue
            sqm_list.append(circ.sqm)
        if len(sqm_list) > 0:
            pds = pd.Series(sqm_list)
            avg = pds.mean()
            loc_sqm_list.append(avg)
    if len(loc_sqm_list) > 0:
        pdl = pd.Series(loc_sqm_list)
        loc_sqm_mean = pdl.mean()
        loc_sqm_rms = pdl.std() if len(loc_sqm_list) > 1 else None
    else:
        return None, None
    
    return loc_sqm_mean, loc_sqm_rms


def get_effective_bortle(sqm):
    if sqm is None:
        return -1.
    if sqm >= 21.99:
        return 1.0
    elif sqm > 21.89:
        return 2. + (21.99 - sqm) / 1.0
    elif sqm >= 21.69:
        return 3. + (21.89 - sqm) / 0.2
    elif sqm >= 20.49:
        return 4. + (21.69 - sqm) / 1.2
    elif sqm >= 19.50:
        return 5. + (20.49 - sqm) / 1.49
    elif sqm >= 18.94:
        return 6. + (19.50 - sqm) / 0.56
    elif sqm >= 18.38:
        return 7. + (18.94 - sqm) / 0.56
    elif sqm >= 16:
        return 8.
    else:
        return 9.