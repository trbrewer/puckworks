"""WP6 — the matched physical-vs-proxy discrimination harness
(analysis.lateral_coupling_discrimination): determinism of the generated artifacts, full grid
coverage, the mirror/identical structural results, the EXACT Xi closed form and continuous-alpha
share match, that the proxy exposes no physical pressure observable, that alpha and Lambda are
kept INDEPENDENT (no alpha=f(Lambda) mapping), and the stale/regenerate contract.
"""
import json

from puckworks.analysis import lateral_coupling_discrimination as D


def test_generation_is_deterministic():
    a = D.generate()
    b = D.generate()
    assert a == b                                            # byte-identical across calls
    for name, content in a.items():
        assert "GENERATED" in content or "generated" in content.lower()   # banner present
    # no generation timestamp leaks into the JSON payload
    doc = json.loads(a["lateral_coupling_discrimination.json"])
    assert "timestamp" not in json.dumps(doc).lower()
    assert doc["content_sha256"] == D._build()["content_sha256"]


def test_every_case_and_lambda_present():
    doc = D._build()
    got = {(r["case_id"], r["lambda_legacy_nominal"]) for r in doc["rows"]}
    want = {(c.case_id, lam) for c in D.CASES for lam in D.LAMBDA_GRID}
    assert got == want
    assert len(doc["rows"]) == len(D.CASES) * len(D.LAMBDA_GRID)
    # legacy nominal boundary sweep around 0.05/5 is carried separately
    assert len(doc["boundary_rows"]) == len(D.CASES) * len(D.BOUNDARY_LAMBDAS)


def test_gap_closed_form_matches_numeric_everywhere():
    # gap/gap0 = 1/(1+Xi) must verify against the solved gap for every row (incl. boundary)
    for r in D._build()["rows"] + D._build()["boundary_rows"]:
        assert r["gap_closed_form_matches_numeric"] is True


def test_isoresistive_mirror_distinguished_by_s0_half_structure():
    # the uncoupled proxy share s0 is EXACTLY 0.5, so the proxy share is alpha-invariant; any
    # physical outlet share != 0.5 is therefore unreachable by the proxy at any alpha.
    rows = {r["lambda_legacy_nominal"]: r for r in D._build()["rows"]
            if r["case_id"] == "isoresistive_mirror"}
    assert rows[0.0]["mathematically_distinguishable"] is False   # uncoupled: identical
    for lam in (0.5, 1.0, 5.0):
        r = rows[lam]
        assert r["uncoupled_proxy_share_1"] == 0.5
        assert r["proxy_share_alpha_invariant"] is True
        assert r["continuous_share_match_possible"] is False      # 0.5 unreachable-from target
        assert r["mathematically_distinguishable"] is True
        assert r["Q_over_Q0"] > 1.0                               # coupling raises total flow
        assert r["q_lat_1to2"] != 0.0                             # real transverse flux


def test_continuous_share_match_not_a_grid_artifact():
    # top_contrast has s0 != 0.5, so its share IS continuously matchable (alpha_star in [0,1]);
    # the case is nevertheless distinguishable via Q/Q0 -- NOT because of a between-grid miss.
    r = next(r for r in D._build()["rows"]
             if r["case_id"] == "top_contrast_only" and r["lambda_legacy_nominal"] == 0.5)
    assert r["proxy_share_alpha_invariant"] is False
    assert r["continuous_share_match_possible"] is True          # share alone IS matchable
    assert 0.0 <= r["alpha_star_continuous"] <= 1.0
    assert r["Q_over_Q0"] > 1.0
    assert r["joint_match_possible"] is False                    # ...but Q/Q0 breaks the joint
    assert r["mathematically_distinguishable"] is True


def test_identical_paths_reports_no_lateral_effect():
    for r in [r for r in D._build()["rows"] if r["case_id"] == "identical_paths"]:
        assert r["q_lat_1to2"] == 0.0                        # negative control: never any flux
        assert r["mathematically_distinguishable"] is False
        assert r["pressure_gap_class"] == "not_applicable"   # gap0 == 0 -> N/A, not "0% reduction"


def test_three_notions_kept_separate():
    # representational non-equivalence is always true; practical resolvability is always OPEN
    for r in D._build()["rows"]:
        assert r["representational_non_equivalence"] is True
        assert r["practical_experimental_resolvability"] is None


def test_proxy_exposes_no_physical_pressure_observable():
    # the discrimination is honest: physical-only observables are absent from the proxy, not 0
    p = D.frozen_two_path_proxy(D.P_IN, 3.0, 1.0, 1.0, 3.0, alpha=0.5)
    assert p["physical_observables_available"] is False
    assert all(v is None for v in p["physical_observables"].values())


def test_no_alpha_to_lambda_mapping():
    # the proxy takes alpha and never Lambda; the physical model takes G_lat (Lambda*g_ax) and
    # never alpha. They are searched independently -> no fitted correspondence.
    import inspect
    proxy_params = inspect.signature(D.frozen_two_path_proxy).parameters
    assert "alpha" in proxy_params and "Lambda" not in proxy_params and "G_lat" not in proxy_params
    phys_params = inspect.signature(D.lc.model1_two_path).parameters
    assert "G_lat" in phys_params and "alpha" not in phys_params
    # the authoritative share match is the closed-form continuous alpha_star, not a grid scan
    src = inspect.getsource(D.physical_row)
    assert "alpha_star_continuous" in src and "0.5 - s0" in src


def test_conservation_holds_across_the_grid():
    for r in D._build()["rows"]:
        assert abs(r["global_residual"]) < 1e-6              # deterministic analytic solve ~ 0


def test_generated_artifacts_stale_then_fresh(tmp_path):
    # writing produces up-to-date files; corrupting one makes verify() flag exactly it; a
    # rewrite makes it clean again.
    D.write(root=tmp_path)
    assert D.verify(root=tmp_path) == []
    target = tmp_path / D.GEN_REL / "lateral_coupling_discrimination.md"
    target.write_text(target.read_text() + "\nHAND EDIT\n", encoding="utf-8")
    assert "lateral_coupling_discrimination.md" in D.verify(root=tmp_path)
    D.write(root=tmp_path)
    assert D.verify(root=tmp_path) == []
