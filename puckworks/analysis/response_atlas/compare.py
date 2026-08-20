def classify_candidate(*, sign_agrees, ordering_agrees, grind_agrees, comparable=True, rmse=None):
    """Gate ordering is deliberate: aggregate error cannot rescue a primary failure."""
    if not comparable: return "SEMANTIC_OR_NONCOMPARABLE"
    if not sign_agrees: return "SIGN"
    if not ordering_agrees: return "MAGNITUDE"
    if not grind_agrees: return "CURVATURE_OR_REGIME"
    return "PARAMETER_UNCERTAINTY_EXPLAINED" if rmse is not None else "MAGNITUDE"

def minimal_sets(pairs, coverage):
    from itertools import combinations
    channels=sorted(coverage)
    for n in range(1,len(channels)+1):
        found=[]
        for combo in combinations(channels,n):
            if all(any(pair in coverage[c] for c in combo) for pair in pairs): found.append(list(combo))
        if found: return found
    return "NO_COMPLETE_MEASUREMENT_SET"
