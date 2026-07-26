"""maille2024.two_regime — the two-exponential early-time extraction kinetics (card Eqs 6.1/6.2).

    (6.1)  C_t/C_inf = phi (1 - e^(-t/lambda_fast)) + (1 - phi)(1 - e^(-t/lambda_slow))
    (6.2)  the same with a delay: t -> (t - tau), applied to caffeine and 3-CQA only

phi enters FIXED from `maille2024.phi_closure` (it is not a free parameter); the regression is two
parameters, lambda_fast and lambda_slow, run independently for each of ~79 material x compound
combinations. So these lambdas are PER-MATERIAL CURVE FITS, not material properties -- they
transfer nowhere on their own, which is exactly what the gate-4 portability probes demonstrate.

WHAT THIS COMPONENT CANNOT DO (card "Interface mapping"): it produces normalized per-species
C_t/C_inf and nothing else. `ShotResultState.EY_pct` and `tds_pct` are UNREACHABLE -- there is no
solute inventory and no total-solids measurement anywhere in the source, and C_inf is MEASURED at
600 s, never predicted. It is a batch, stirred, atmospheric, bed-free, flow-free, coarse-grind
model: calibration and gate provider only.

tau is NOT tabulated anywhere in the thesis. The card records the text's visual-inspection values
(~4 s caffeine, ~3 s 3-CQA, 0 for the three acids) and flags that the first ~5 s are unobserved, so
tau may be a detection-limit artifact rather than a hydration delay -- CLAUDE.md rule "no parameters
invented where a card says 'not provided'" means these stay labelled visual, never fitted.
"""
import math

# Card Parameters: tau is "not provided" as a table. These are the text's visual-inspection values.
TAU_S = {"Caffeine": 4.0, "3-CQA": 3.0, "Citric acid": 0.0, "Malic acid": 0.0, "Quinic acid": 0.0}

# The observed timescale bands across all materials/species (Tables 6.4/6.5). These are the source's
# EMPIRICAL RANGE, not a physical law -- gate 4 tests whether other rigs land inside them.
LAM_FAST_RANGE = (2.2, 19.1)
LAM_SLOW_RANGE = (13.0, 158.0)

# Validity envelope (card "Regime boundaries"): the fitted materials are DRIP-COARSE.
VALID_D43_UM = (537.0, 1540.0)
BREW_TEMPERATURE_C = 91.5
BREW_RATIO_G_PER_ML = 0.028


def fraction_extracted(t_s, phi, lam_fast_s, lam_slow_s, tau_s=0.0):
    """Eq 6.2 (Eq 6.1 when tau=0): normalized concentration C_t/C_inf at time `t_s`.

    Returns exactly 0 for t <= tau -- the source models the delay as a hard shift, with no
    extraction before it. That is a modelling choice the card flags as suspect (the first ~5 s are
    unobserved), not an observation."""
    if not (0.0 <= phi <= 1.0):
        raise ValueError("two_regime: phi must be a fraction in [0, 1], got %r" % (phi,))
    if lam_fast_s <= 0 or lam_slow_s <= 0:
        raise ValueError("two_regime: time constants must be positive, got (%r, %r)"
                         % (lam_fast_s, lam_slow_s))
    if t_s <= tau_s:
        return 0.0
    x = t_s - tau_s
    return (phi * (1.0 - math.exp(-x / lam_fast_s))
            + (1.0 - phi) * (1.0 - math.exp(-x / lam_slow_s)))


def kinetics(sample_id):
    """Per-compound (lambda_fast, lambda_slow) [s] for one material, from Tables 6.4 + 6.5.

    Compounds whose fit is unreported ('*' in the source -- Omega_C/M/O quinic) are omitted rather
    than defaulted. Rows whose 95% CI is internally impossible (E5) are still returned: the CI is
    unusable, the point estimate is not. `ci_flags()` surfaces which."""
    from puckworks import data as d
    c = {r["Sample ID"]: r for r in d.maille_kinetics_caffeine_3cqa()}.get(sample_id)
    a = {r["Sample ID"]: r for r in d.maille_kinetics_organic_acids()}.get(sample_id)
    out = {}
    for row, compounds in ((c, ("Caffeine", "3-CQA")), (a, ("Citric", "Malic", "Quinic"))):
        if row is None:
            continue
        for comp in compounds:
            try:
                lf = float(row["%s lambda_fast (s)" % comp])
                ls = float(row["%s lambda_slow (s)" % comp])
            except (KeyError, TypeError, ValueError):
                continue          # '*' = unreported in the source; not defaulted
            out[comp] = (lf, ls)
    return out


def ci_flags():
    """E5: the rows whose published 95% CI does not bracket its own point estimate.

    Two exist (Omega_T / 3-CQA lambda_fast, upper 11.9 < estimate 12.2; Omega_L / quinic
    lambda_slow, [65, 54] around 44). Both are internally impossible and their CIs are UNUSABLE --
    carried as flags, never corrected (the card's standing rule: flag errata, do not fix them)."""
    from puckworks import data as d
    flagged = []
    n_rows = 0
    specs = [(d.maille_kinetics_caffeine_3cqa(), ("Caffeine", "3-CQA")),
             (d.maille_kinetics_organic_acids(), ("Citric", "Malic", "Quinic"))]
    for rows, compounds in specs:
        for r in rows:
            n_rows += 1
            for comp in compounds:
                for regime in ("lambda_fast", "lambda_slow"):
                    try:
                        est = float(r["%s %s (s)" % (comp, regime)])
                        lo = float(r["%s %s lower 95CI" % (comp, regime)])
                        hi = float(r["%s %s upper 95CI" % (comp, regime)])
                    except (KeyError, TypeError, ValueError):
                        continue
                    if lo > est or hi < est:
                        flagged.append(dict(sample=r["Sample ID"], compound=comp, regime=regime,
                                            est=est, lower=lo, upper=hi))
    return dict(n_rows_scanned=n_rows, flagged=flagged)


def in_source_bands(lam_fast_s, lam_slow_s):
    """Do a candidate pair of time constants land inside the source's observed bands?

    The gate-4 portability question in one call. A MISS is the informative outcome: it says the
    two-regime decomposition does not port off maille's rig. A HIT would NOT establish portability
    either -- numerical overlap is not semantic equivalence (see the producers' portability_vector)."""
    return dict(fast_in_band=bool(LAM_FAST_RANGE[0] <= lam_fast_s <= LAM_FAST_RANGE[1]),
                slow_in_band=bool(LAM_SLOW_RANGE[0] <= lam_slow_s <= LAM_SLOW_RANGE[1]),
                fast_range_s=list(LAM_FAST_RANGE), slow_range_s=list(LAM_SLOW_RANGE))
