def discriminate(left_interval, right_interval, measurement_uncertainty):
    if measurement_uncertainty == "NOT_PROVIDED": return "NOT_ADJUDICATED_MISSING_UNCERTAINTY"
    if left_interval is None or right_interval is None: return "UNSUPPORTED"
    u=float(measurement_uncertainty)
    l=(left_interval[0]-u,left_interval[1]+u); r=(right_interval[0]-u,right_interval[1]+u)
    return "ROBUSTLY_DISCRIMINATING" if l[1] < r[0] or r[1] < l[0] else "NOT_DISCRIMINATING"
