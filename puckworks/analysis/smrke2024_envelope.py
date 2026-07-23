"""smrke2024 EY(t) envelope + cameron shot-morphology check (the S-A qualitative gate).

Background — why this module exists instead of the card's original gate
------------------------------------------------------------------------
smrke2024's Impl-est proposed a single consumer gate: an extraction config at
20 g / 40 g / 9 bar must land its (EY, t_shot) pairs on the Fig-3 curve within
its scatter (~+/-0.5 pt EY at fixed t). That point-match is NOT honestly
assertable across setups: cameron2020 is calibrated on Cameron's coffee/EK43
grind/machine; smrke's Fig-3 is a DIFFERENT coffee, grinder (Bentwood), and
machine, and smrke's absolute EY (16.4-21.3 %) is setup-specific. The +/-0.5 pt
window is TIGHTER than the cross-setup EY spread, so a landing would be
coincidence and forcing it (loosening the tolerance, cherry-picking conditions)
would be exactly the fudge the card labels are meant to catch.

The card is therefore re-scoped into two named gates (see docs/cards/smrke2024.md):

  * S-A (buildable today, this module + gate_smrke2024_fast_extraction_shape):
    a qualitative/verification shape check -- cameron's EY(t) has the
    fast-rise-then-plateau morphology, its grind sweep traces the same
    EY-vs-t_shot SLOPE SIGN as smrke's Fig-3 master curve, it reaches >=80 % of
    its own final yield by t=15 s (a necessary-not-sufficient fast-extraction
    sanity check -- the ONE clause of the original gate that survives
    cross-setup transfer intact), and its plateau lands in a plausible espresso
    EY band that brackets smrke's observed ceiling. This is qualitative_capacity
    strength. It does NOT claim to reproduce smrke's curve.

  * S-B (blocked, quantitative): the true +/-0.5 pt point-match. Unblock
    conditions are written on the card: a defensible smrke-grind -> extraction
    grain-size adapter plus ceiling calibration (the G5 grind-transfer gap), OR
    smrke's raw (EY, t, PSD) data (available on request, smrk@zhaw.ch), which
    would let the comparison be made in smrke's own setup terms.

EY_MAX_SMRKE below parks the digitized Fig-3 ceiling as a smrke-specific
parameter -- a prerequisite for any future S-B attempt and the band anchor S-A
reports its cross-coffee offset against.
"""
from __future__ import annotations

import numpy as np

# smrke2024 Fig-3, digitized ceiling. Paper text says "16.5-21.5 %"; the digitized
# markers span 16.41-21.31. This is smrke's coffee/recipe-specific max extraction
# yield -- NOT transferable to another coffee. Parked here as the S-B ceiling
# parameter and the S-A band anchor.
EY_MAX_SMRKE = 21.3        # % (digitized Fig-3 max; paper text ~21.5)
EY_MIN_SMRKE = 16.4        # % (digitized Fig-3 min)
T_MIN_SMRKE = 8.2          # s
T_MAX_SMRKE = 79.5         # s

# A plausible espresso EY band the cameron plateau must fall inside. Deliberately
# generous: it is a "nothing is broken" sanity band that BRACKETS smrke's
# observed ceiling, NOT a point-match to it. cameron's own coffee extracts a few
# points below smrke's, which is expected cross-coffee and is REPORTED (not
# asserted against) as `plateau_offset_vs_smrke_pct`.
EY_BAND_PCT = (12.0, 28.0)

# The canonical cameron grind sweep for the shape check: in-range EK43 dials at
# smrke's 9-bar / 20 g:40 g recipe, each giving a shot long enough that t=15 s is
# interior (t_shot ~16-20 s here).
GS_SWEEP = (1.3, 1.5, 1.7)
P_BAR = 9.0
M_IN = 0.020
M_OUT = 0.040


def smrke_envelope():
    """Return smrke's digitized Fig-3 envelope (EY/t spans + ceiling) and the
    observed fast-extraction fraction of smrke's own early shots. The ceiling
    (EY_MAX_SMRKE) is the smrke-specific parameter parked for S-B."""
    from puckworks import data as d
    f3 = d.smrke2024_figures()["fig3_ey_vs_time"]
    ey = np.array([float(r["extraction_pct"]) for r in f3 if r.get("extraction_pct")])
    t = np.array([float(r["extraction_time_s"]) for r in f3 if r.get("extraction_time_s")])
    early = ey[t <= 15.0]
    return dict(
        ey_max=EY_MAX_SMRKE, ey_min=EY_MIN_SMRKE, t_min=T_MIN_SMRKE, t_max=T_MAX_SMRKE,
        n_points=int(ey.size),
        ey_digitized_max=float(ey.max()), ey_digitized_min=float(ey.min()),
        # smrke's OWN early shots reach this fraction of the ceiling by t<=15 s --
        # the empirical anchor for the S-A >=0.80 fast-extraction clause.
        early_frac_vs_ceiling=(float(early.min() / EY_MAX_SMRKE),
                               float(early.max() / EY_MAX_SMRKE)),
    )


def cameron_shot_morphology(gs: float, p_bar: float = P_BAR):
    """Run one cameron2020 shot and summarize its EY(t) morphology.

    Returns monotonicity, deceleration (first-half vs second-half rate), the
    fraction of the final yield reached by t=15 s, and the plateau EY. No smrke
    coupling here -- cameron runs at its OWN coffee/grind; the gate compares only
    SHAPE and slope sign, never absolute EY, to smrke."""
    from puckworks.models.cameron2020 import extraction_bdf as cam
    r = cam.simulate_shot(gs=gs, p_bar=p_bar, m_in=M_IN, m_out=M_OUT)
    t = np.asarray(r.t)
    ey = 100.0 * np.asarray(r.m_cup) / r.m_in
    ey_final = float(ey[-1])
    t_shot = float(t[-1])
    monotone = bool(np.all(np.diff(ey) >= -1e-9))
    # fast-rise-then-plateau: mean extraction rate in the first half exceeds the second half
    half = t_shot / 2.0
    ey_half = float(np.interp(half, t, ey))
    rate_early = float((ey_half - ey[0]) / (half - t[0]))
    rate_late = float((ey_final - ey_half) / (t_shot - half))
    decelerating = bool(rate_early > rate_late)
    # fraction of final yield reached by 15 s (only meaningful when 15 s is interior)
    ey_15 = float(np.interp(15.0, t, ey)) if t_shot >= 15.0 else float("nan")
    frac_15 = ey_15 / ey_final if ey_final > 0 else float("nan")
    return dict(gs=gs, t_shot=round(t_shot, 1), ey_final=round(ey_final, 2),
                ey_15=round(ey_15, 2), frac_15=round(frac_15, 3),
                monotone=monotone, decelerating=decelerating,
                rate_early=round(rate_early, 3), rate_late=round(rate_late, 3))


def shape_report():
    """Evaluate the full S-A shape check across the canonical grind sweep and
    return the per-shot morphology plus the sweep-level EY-vs-t_shot slope-sign
    match to smrke's Fig-3 master curve. Consumed by
    gate_smrke2024_fast_extraction_shape."""
    env = smrke_envelope()
    shots = [cameron_shot_morphology(gs) for gs in GS_SWEEP]
    # sweep slope sign: order shots by shot time; smrke's Fig-3 rises (longer shot -> higher EY),
    # so cameron's plateau should be non-decreasing in t_shot (same slope SIGN, not magnitude).
    ordered = sorted(shots, key=lambda s: s["t_shot"])
    ey_by_t = [s["ey_final"] for s in ordered]
    slope_sign_matches = all(b >= a - 1e-9 for a, b in zip(ey_by_t, ey_by_t[1:]))
    lo, hi = EY_BAND_PCT
    for s in shots:
        s["in_band"] = bool(lo <= s["ey_final"] <= hi)
        # reported, NOT asserted: cameron's cross-coffee offset from smrke's ceiling
        s["plateau_offset_vs_smrke_pct"] = round(
            100.0 * (s["ey_final"] - env["ey_max"]) / env["ey_max"], 1)
    return dict(env=env, shots=shots, ordered_ey_by_t=ey_by_t,
                slope_sign_matches=bool(slope_sign_matches))
