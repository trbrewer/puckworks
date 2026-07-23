"""gagne2021 apparent-resistance decline vs the liquor-viscosity hypothesis — DISCRIMINATION.

Gagné 2021 attributes the monotonic post-bloom decline in DE1 apparent puck resistance to the
slurry/liquor viscosity falling as effluent TDS falls (μ(T, TDS)), not to bed compaction/swelling
or fines. This module computes, from the 11 published `.shot` traces, the observed post-bloom
apparent-resistance decline R(t) = P(t)/Q(t), and bounds the viscosity contribution using the
transcribed telisromero2001 μ(T, X_w) closure at both the bulk shot-TDS and Gagné's own
reconstructed early first-drip TDS.

The result is a DISCRIMINATION, not a validation: the observed decline is quantitatively
well-matched by a μ(TDS) decline over the shot's TDS trajectory — the telisromero μ ratio is ~2.7×
at Gagné's reconstructed ~15% early first-drip TDS (≈ the observed decline) and ~1.6× at bulk
shot-TDS — so the viscosity-decline hypothesis is ADMISSIBLE. But it is DEGENERATE with a
bed-compaction/swelling explanation, and the traces alone (no independent TDS(t)) cannot separate
them. (Note: the local μ ratio here is NOT the G10 *shot-integrated* Darcy error — that ≤~1.05%
figure averages over the mostly-dilute bed; the apparent-resistance decline is dominated by the
early high-TDS liquor.) Gagné's own EY(t) reconstruction is endpoint-anchored and circular (card
`gagne2021.md`). NOT a registered component; NOT a validated κ(t) law.
"""
import numpy as np

from puckworks import data as _data

_BLOOM_END_S = 42.0        # bloom is 10-40 s; take the established-flow window after it
_MIN_FLOW = 0.3            # g/s — established flow
_MIN_PRESSURE = 1.0        # bar
_BREW_T_K = 365.15         # ~92 C brew temperature (gagne temperature goal)


def observed_resistance_decline():
    """Per-shot post-bloom apparent-resistance decline ratio (peak R / end-of-shot R), R = P/Q,
    over the established-flow window. Returns dict with the per-shot ratios and their median/range."""
    ratios = []
    for sid, ch in _data.gagne2021_shots().items():
        t, P, Q = ch["espresso_elapsed"], ch["espresso_pressure"], ch["espresso_flow"]
        win = (t >= _BLOOM_END_S) & (Q > _MIN_FLOW) & (P > _MIN_PRESSURE)
        if int(win.sum()) < 8:
            continue
        R = P[win] / Q[win]
        Rs = np.convolve(R, np.ones(3) / 3.0, mode="valid")     # light smoothing
        ratios.append(float(Rs.max() / Rs[-5:].mean()))         # peak vs end-of-shot
    ratios = np.array(sorted(ratios))
    return dict(n_shots=int(ratios.size), ratios=ratios,
                median=float(np.median(ratios)),
                lo=float(ratios.min()), hi=float(ratios.max()))


def viscosity_ratio(tds_pct):
    """telisromero2001 dynamic-viscosity ratio μ(TDS)/μ(water) at the brew temperature."""
    Xw = 100.0 - float(tds_pct)
    return (_data.telisromero_viscosity_pas(_BREW_T_K, Xw)
            / _data.telisromero_viscosity_pas(_BREW_T_K, 100.0))


def discrimination():
    """Bound the viscosity contribution against the observed decline. Returns the observed decline,
    the μ ratio at bulk shot-TDS (~5-10%) and at Gagné's reconstructed early TDS (~15%), and the
    degeneracy verdict."""
    obs = observed_resistance_decline()
    mu_bulk = viscosity_ratio(7.5)                 # ~bulk shot TDS (5-10%)
    mu_early = viscosity_ratio(15.0)               # Gagné's reconstructed early first-drip TDS
    # the observed decline is quantitatively consistent with a mu(TDS) decline from ~15% early TDS
    viscosity_admissible = 0.75 * obs["median"] <= mu_early <= 1.30 * obs["median"]
    # ...but the same magnitude is reachable by a bed mechanism; no independent TDS(t) here
    degenerate_with_bed = True
    return dict(
        observed=obs, mu_ratio_bulk=mu_bulk, mu_ratio_early=mu_early,
        viscosity_admissible=viscosity_admissible, degenerate_with_bed=degenerate_with_bed,
    )
