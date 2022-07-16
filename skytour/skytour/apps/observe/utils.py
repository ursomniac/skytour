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