"""Fast structural guards for Paper A observable contracts (review AR-06/MAJ-08).

These do NOT run PDE solves (the slow analyses stay out of CI); they pin the
matched-endpoint contract so a whole-cup path cannot silently revert to a fixed
integration time when the manuscript claims a fixed beverage mass.
"""
import inspect

from puckworks.validation.slow import angeloni_bracket as ab


def test_matched_bounds_is_mass_consistent():
    """t_end = 40 mL / flow, integrated from 0 (review B1/MAJ-08/MAJ-09)."""
    assert ab._V_TARGET_ML == 40.0
    lo, hi = ab._matched_bounds(2.0)
    assert lo == 0.0 and abs(hi - 20.0) < 1e-9        # 40 mL / 2 mL/s = 20 s
    lo, hi = ab._matched_bounds(1.6)
    assert abs(hi - 25.0) < 1e-9                        # 40 / 1.6 = 25 s


def test_paper_a_build_verifies_manuscript_claims():
    """review A2-05/A2-13: the strict build must confirm every manuscript-facing
    headline number equals the value in the results bundle (fails on drift). Runs
    against the cached bundle (fast); guards the manuscript<->bundle contract."""
    from puckworks.paper_a.build import verify
    ok, failures, manifest = verify(timestamp=None, write_manifest=False)
    assert ok, "manuscript numbers drifted from the bundle: " + "; ".join(failures)
    assert manifest["n_claims"] >= 12 and manifest["n_failures"] == 0
    assert all(v != "MISSING" for v in manifest["data_sha256"].values())


def test_waszkiewicz_sensitivity_localization_invariant():
    """review A2-13b: the external-panel bundle must carry the nuisance sweep and it
    must report the localization conclusion INVARIANT (every temp x floor cell keeps
    the fraction range ratio >1, cup never discriminates). Reads the committed bundle
    (fast); the sweep itself is slow and runs in the Paper A `full` build."""
    import json
    import os
    bundle = os.path.join("docs/figures/paper_a/results.json")
    if not os.path.exists(bundle):
        import pytest
        pytest.skip("Paper A bundle not present")
    with open(bundle) as f:
        s = json.load(f).get("external_waszkiewicz_sensitivity")
    if s is None:
        import pytest
        pytest.skip("sensitivity block not in this bundle (recompute with `full`)")
    assert s["localization_invariant"] is True
    assert s["fraction_range_ratio_min"] > 1.0
    assert all(c["cup_carries_no_rate_info"] for c in s["cells"])


def test_discrepancy_control_dose_response():
    """review MAJ-13: the bundle must carry the model-discrepancy positive control as a
    DOSE-RESPONSE. Moderate discrepancy leaves an irreducible floor above noise while the
    located rate stays robust near 1.0; the larger dose BIASES the located rate off 1.0.
    Reads the committed bundle (fast); the control is slow and runs in the `full` build."""
    import json
    import os
    bundle = "docs/figures/paper_a/results.json"
    if not os.path.exists(bundle):
        import pytest
        pytest.skip("Paper A bundle not present")
    with open(bundle) as f:
        b = json.load(f)
    mod = b.get("full_cup_discrepancy"); lrg = b.get("full_cup_discrepancy_large")
    if mod is None or lrg is None:
        import pytest
        pytest.skip("discrepancy control not in this bundle (recompute with `full`)")
    # moderate: irreducible floor exceeds the 3% noise; located rate still mostly at 1.0
    assert mod["mean_irreducible_frac_mape_floor"] > 3.0
    assert mod["mean_located_rate_biased_fraction"] < 0.5
    # larger dose: floor persists AND the located rate is now biased off 1.0
    assert lrg["mean_located_rate_biased_fraction"] > mod["mean_located_rate_biased_fraction"]
    assert lrg["per_solute"]["caffeine"]["frac_best_rate_median"] != 1.0


def test_mape_level_returns_pair_and_profile_is_1d():
    """review A2-01: _mape_level returns (level, MAPE%); a MAPE profile must take the
    [1] element so it is 1-D, not a mix of levels and MAPEs. Guards the tuple bug."""
    import numpy as np
    f = np.array([1.0, 2.0, 3.0]); m = np.array([1.1, 2.2, 2.7])
    pair = ab._mape_level(f, m)
    assert isinstance(pair, tuple) and len(pair) == 2
    c, mape = pair
    assert mape >= 0.0
    # a profile over several 'rates' (scaled f) must be 1-D when taking [1]
    prof = np.array([ab._mape_level(f * s, m)[1] for s in (0.5, 1.0, 2.0)])
    assert prof.ndim == 1 and prof.shape == (3,)
    assert float(np.min(prof)) == min(prof)            # min is over MAPEs only


def test_species_bracket_has_no_fixed_time_param():
    """The pooled species bracket must not expose a fixed t_shot_s knob -- it now
    integrates to the matched 40 mL endpoint (review MAJ-08)."""
    params = inspect.signature(ab.gate_pannusch_angeloni_species_bracket).parameters
    assert "t_shot_s" not in params
    src = inspect.getsource(ab.gate_pannusch_angeloni_species_bracket)
    assert "_matched_bounds" in src                    # uses the matched endpoint
    assert "[0.0, t_shot_s]" not in src                # not the old fixed-time bounds
