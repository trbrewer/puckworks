"""smrke2024 S-A qualitative gate + envelope bookkeeping.

Verifies the re-scoped consumer gate: cameron's EY(t) has the fast-rise/plateau morphology and
Fig-3 slope sign, WITHOUT claiming the deferred S-B point-match. See docs/cards/smrke2024.md and
puckworks/analysis/smrke2024_envelope.py for why the original +/-0.5 pt gate is cross-setup-blocked.
"""
from puckworks.analysis import smrke2024_envelope as se
from puckworks.validation.gates import gate_smrke2024_fast_extraction_shape


def test_envelope_reads_smrke_ceiling():
    env = se.smrke_envelope()
    assert env["n_points"] == 46
    # digitized ceiling ~= the parked EY_MAX_SMRKE parameter (paper text ~21.5%)
    assert abs(env["ey_digitized_max"] - se.EY_MAX_SMRKE) < 0.2
    # smrke's own early shots reach 0.77-0.83 of ceiling by t<=15 s (the S-A >=0.80 anchor)
    lo, hi = env["early_frac_vs_ceiling"]
    assert 0.74 <= lo <= 0.80 <= hi <= 0.86


def test_shape_morphology_is_fast_rise_then_plateau():
    r = se.shape_report()
    for s in r["shots"]:
        assert s["monotone"]
        assert s["decelerating"]                     # first-half rate > second-half rate
        assert s["frac_15"] >= 0.80                  # >=80% of own final yield by 15 s
        assert s["in_band"]                          # plateau in the espresso sanity band
        assert s["plateau_offset_vs_smrke_pct"] < 0  # cross-coffee: cameron below smrke ceiling
    # slope sign matches smrke's rising Fig-3 master curve (longer shot -> higher EY)
    assert r["slope_sign_matches"]


def test_gate_passes_and_declares_qualitative_only():
    res = gate_smrke2024_fast_extraction_shape()
    assert res["passed"]
    # the gate must NOT claim the S-B point-match; strength is a weak qualitative/compatibility tier
    assert "sign_or_compatibility" in res["strength"]
    assert "S-B" in res["strength"] and "BLOCKED" in res["strength"]
