

def compile_times(times):
    t0 = times[0][0]
    at = t0
    tlist = []
    
    for t in times:
        # time since start
        dt0 = t[0] - t0
        dt = t[0] - at
        tlist.append((t[0], dt, dt0, t[1]))
        at = t[0]
    return tlist