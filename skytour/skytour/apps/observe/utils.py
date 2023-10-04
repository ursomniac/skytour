import pandas as pd
def get_mean_obs_sqm(loc, include_moon=False, debug=True):

    sessions = loc.observingsession_set.all()
    #print(f"There are {len(sessions)} sessions.")
    loc_sqm_list = []
    for session in sessions:
        circumstances = session.observingcircumstances_set.all()
        sqm_list = []
        for circ in circumstances:
            if not circ.sqm or not circ.use_sqm:
                continue
            if circ.moon and not include_moon:
                continue
            #if debug:
            #    print(f"Adding: {circ.sqm} to list ({circ.moon})")
            sqm_list.append(circ.sqm)
        #print(f"Session: {session} has {len(sqm_list)} measures")
        if len(sqm_list) > 0:
            pds = pd.Series(sqm_list)
            avg = pds.mean()
            loc_sqm_list.append(avg)
    #print(f"There are {len(loc_sqm_list)} session measurements")
    if len(loc_sqm_list) > 0:
        pdl = pd.Series(loc_sqm_list)
        loc_sqm_mean = pdl.mean()
        loc_sqm_rms = None if len(loc_sqm_list) < 2 else pdl.std()
    else:
        return None, None
    
    return loc_sqm_mean, loc_sqm_rms

    
def get_effective_bortle(sqm):
    if sqm is None:
        return -1.
    if sqm > 21.99:    # Bortle 1:  SQM > 21.99
        return 1.0
    elif sqm >= 21.89:  # Bortle 2:  SQM 21.89 to 21.99
        p = (21.89 - sqm) / 0.1
        x = 3. + p
    elif sqm >= 21.69:  # Bortle 3: SQM 21.69 - 21.89
        p = (21.69 - sqm) / 0.2
        x = 4. + p
    elif sqm >= 20.49:  # Bortle 4: SQM 20.49 - 21.69
        p = (20.49 - sqm) / 1.2
        x = 5. + p
    elif sqm >= 19.50:  # Bortle 5: SQM 19.50 - 20.49
        p = (19.50 - sqm) / 1.0
        x = 6. + p
    elif sqm >= 18.94:  # Bortle 6: SQM 18.94 - 19.50
        p = (18.94 - sqm) / 0.56
        x = 7. + p
    elif sqm >= 17.00: # Bortle 7: SQM 17.00 - 18.94
        p = (17. - sqm) / 1.94
        x = 8. + p
    elif sqm >= 15.00:  # Bortle 8: SQM 15-17
        p = (15. - sqm) / 2.0
        x = 9 + p
    else:
        x = 9.0
    return x
