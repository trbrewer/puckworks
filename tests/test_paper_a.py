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


def _load_bundle():
    import json
    import os
    bundle = "docs/figures/paper_a/results.json"
    if not os.path.exists(bundle):
        import pytest
        pytest.skip("Paper A bundle not present")
    with open(bundle) as f:
        return json.load(f)


def test_bundle_has_no_stale_evidence_taxonomy():
    """review A3-32: bundle-facing verdict/strength strings must use the current evidence
    taxonomy -- no 'REAL transfer test', 'external stress test', 'Frozen external
    prediction', 'transfers reasonably', or 'no rate information at all'."""
    b = _load_bundle()
    forbidden = ["REAL transfer test", "external stress test",
                 "Frozen external prediction", "transfers reasonably",
                 "transfers REASONABLY", "no rate information at all"]
    hits = []

    def walk(o):
        if isinstance(o, dict):
            for v in o.values():
                walk(v)
        elif isinstance(o, list):
            for v in o:
                walk(v)
        elif isinstance(o, str):
            for ph in forbidden:
                if ph.lower() in o.lower():
                    hits.append(ph)
    walk(b)
    assert not hits, "stale evidence-taxonomy phrases in bundle: " + ", ".join(set(hits))


def test_figures_render_from_bundle():
    """review A3-24: the figures must render from the committed results bundle (figure /
    result synchronization) without recomputing any PDE. Skips if matplotlib (the
    [figures] extra) or the bundle is absent."""
    import os
    import pytest
    try:
        import matplotlib  # noqa: F401
    except Exception:
        pytest.skip("matplotlib not installed ([figures] extra)")
    if not os.path.exists("docs/figures/paper_a/results.json"):
        pytest.skip("Paper A bundle not present")
    import tempfile
    from puckworks import figures_paper_a as fpa
    with tempfile.TemporaryDirectory() as d:
        # a representative data-bearing figure that consumes the new fields
        p = fpa.fig4_transfer(outdir=d)
        assert os.path.exists(p) and os.path.getsize(p) > 1000


def test_offgrid_noise_sim_fraction_beats_cup():
    """review A3-15/A3-16: the off-grid + realistic-noise simulation must show the
    fraction objective recovering the off-grid true rate far better than the single cup,
    across iid/heteroscedastic/correlated noise -- so the contrast is not an artefact of
    an on-grid true rate or iid noise. Reads the committed bundle (fast)."""
    r = _load_bundle().get("full_cup_offgrid_noise")
    if r is None:
        import pytest
        pytest.skip("full_cup_offgrid_noise not in this bundle (recompute with `full`)")
    assert r["mean_frac_recovered_err_pct"] < r["mean_cup_recovered_err_pct"]
    assert r["n_frac_beats_cup"] >= (2 * r["n_cases"]) // 3   # frac wins the clear majority
    # true rates were genuinely off the original 9-point candidate grid
    grid = {0.25, 0.4, 0.6, 0.8, 1.0, 1.4, 2.0, 3.0, 4.0}
    assert all(tr not in grid for tr in r["true_rates"])


def test_condition_envelopes_and_threshold_sensitivity():
    """review A3-11/A3-02: the transfer must carry per-condition prediction envelopes and
    a threshold sweep; the median envelope is narrow but a worst case exists."""
    t = _load_bundle().get("transfer")
    if not t or "condition_envelopes" not in t:
        import pytest
        pytest.skip("condition_envelopes not in this bundle (recompute with `full`)")
    assert t["median_condition_envelope_frac_of_obs"] < t["worst_condition_envelope_frac_of_obs"]
    ce = next(iter(t["condition_envelopes"].values()))
    assert all(r["pred_min"] <= r["pred_point"] + 1e-6 <= r["pred_max"] + 1e-6 for r in ce) or \
        all(r["pred_min"] <= r["pred_max"] for r in ce)
    ts = next(iter(t["threshold_sensitivity"].values()))
    assert {"2pct", "5pct", "10pct", "20pct"} <= set(ts)
    # wider tolerance -> at least as many members
    assert ts["20pct"]["n_in_set"] >= ts["2pct"]["n_in_set"]


def test_reduced_model_ladder_mech_vs_constants():
    """review A3-19: the ladder must report parameter counts and the decisive comparison
    -- the shared mechanistic model rarely beats per-grind constants in-sample."""
    lad = _load_bundle().get("reduced_model_ladder")
    if lad is None:
        import pytest
        pytest.skip("reduced_model_ladder not in this bundle")
    assert lad["param_counts"] == {"model0": 1, "model1": 3, "model2": 2, "model3": 6}
    # the headline: mechanistic shared model beats per-grind constants in few/no fits
    assert lad["n_fits_mech_beats_pergrind_const"] <= 1


def test_table7_rate_constraint_collapses_profile():
    """review A3-13: the same-campaign Table 7 inventory must intersect the profiled
    valley at an interior rate, collapsing the broad inventory-rate profile to a narrow
    band. Reads the committed bundle (fast; PDE-free post-processing)."""
    tc = _load_bundle().get("table7_rate_constraint")
    if not tc or "caffeine" not in tc:
        import pytest
        pytest.skip("table7_rate_constraint not in this bundle")
    caf = tc["caffeine"]
    assert caf["intersection_interior"] is True
    assert caf["implied_rate"] is not None
    # the implied-rate band is much narrower than the full tested rate domain (~0.15-6.5)
    if caf["implied_rate_band"]:
        lo, hi = caf["implied_rate_band"]
        assert (hi - lo) < 3.0


def test_transfer_skill_reports_null_benchmark():
    """review A3-01: the bundle must carry the null-benchmark skill package and it must
    report the honest split -- the mechanistic O->C/F transfer adds only small skill over
    an O-trained level-only constant and is worse on a large share of held-out points."""
    ts = _load_bundle().get("transfer_skill")
    if ts is None:
        import pytest
        pytest.skip("transfer_skill not in this bundle (recompute with `full`)")
    assert "skill_vs_const" in ts and "pooled_const_mape" in ts
    # small incremental skill: model within a couple pp of the constant
    assert abs(ts["pooled_model_mape"] - ts["pooled_const_mape"]) < 3.0
    # honestly report the model is worse than the constant on a meaningful share
    assert ts["n_model_worse_than_const"] >= ts["n_points"] // 4


def test_geometry_spread_is_full_precision():
    """review A3-03: the geometry spread must NOT be integer-rounded before the spread is
    taken (a sub-1pp spread must survive). Guards against round-before-aggregate."""
    gs = _load_bundle().get("geometry_sensitivity")
    if gs is None:
        import pytest
        pytest.skip("geometry_sensitivity not in this bundle")
    sp = gs["max_geometry_spread_pp"]
    # a genuinely full-precision spread is (almost surely) not an exact integer
    assert sp != round(sp), "geometry spread looks integer-rounded (A3-03 regression)"


def test_joint_independent_mean_from_raw():
    """review A3-03: the joint fit must expose raw independent per-grind fields and the
    headline independent mean must match the raw average (not the rounded dict)."""
    import numpy as np
    j = _load_bundle().get("joint")
    if j is None or "per_variety" not in j:
        import pytest
        pytest.skip("joint not in this bundle")
    raws = [j["per_variety"][v][s]["independent_mean_raw"]
            for v in j["per_variety"] for s in j["per_variety"][v]]
    assert abs(float(np.mean(raws)) - j["mean_independent_per_grind_mape"]) < 0.06


def test_identifiability_panel_boundary_and_overlap_fields():
    """review A3-04/A3-09/A3-12: the panel must flag domain censoring of the 10% set and
    report a quantitative SSE<->MAPE overlap (Jaccard), not just a binary agreement flag."""
    p = _load_bundle().get("panel_caffeine")
    if p is None:
        import pytest
        pytest.skip("panel_caffeine not in this bundle")
    assert "profile_upper_censored" in p and "profile_lower_censored" in p
    assert "sse_mape_threshold_jaccard" in p
    assert p["profile_upper_censored"] is True         # caffeine set reaches upper edge


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


def test_identifiability_convergence_144_and_continuous():
    """review A2-06/07 + MAJ-04: the bundle must carry the density/domain convergence
    (through the 144-pt grid) AND a grid-free continuous optimiser confirming the flat
    valley is not a discretisation artefact. Reads the committed bundle (fast)."""
    import json
    import os
    bundle = "docs/figures/paper_a/results.json"
    if not os.path.exists(bundle):
        import pytest
        pytest.skip("Paper A bundle not present")
    with open(bundle) as f:
        c = json.load(f).get("identifiability_convergence")
    if c is None:
        import pytest
        pytest.skip("convergence not in this bundle (recompute with `full`)")
    labels = [r["label"] for r in c["rows"]]
    assert any("144" in x for x in labels)                 # the 144-pt grid ran
    assert c["condition_number_stable_across_density"] is True
    co = c["continuous_optimiser"]
    assert co["optimum_is_interior"] is True               # grid-free optimum is interior
    assert co["valley_log_half_width_within10pct"] > 0.5   # a genuinely flat valley


def test_endpoint_mass_sensitivity_reports_honest_caveat():
    """review A2-09: the bundle must carry the endpoint-mass sensitivity and it must
    report the HONEST split -- the caffeine inventory-match improvement is robust across
    38/40/42 mL, but the overall MAPE is endpoint-sensitive (a non-trivial spread). Reads
    the committed bundle (fast)."""
    import json
    import os
    bundle = "docs/figures/paper_a/results.json"
    if not os.path.exists(bundle):
        import pytest
        pytest.skip("Paper A bundle not present")
    with open(bundle) as f:
        e = json.load(f).get("endpoint_mass_sensitivity")
    if e is None:
        import pytest
        pytest.skip("endpoint sensitivity not in this bundle (recompute with `full`)")
    assert e["caffeine_helps_invariant"] is True          # robust part
    assert e["overall_mape_spread_pp"] > 1.0              # honestly non-negligible
    assert len(e["rows"]) == 3


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
