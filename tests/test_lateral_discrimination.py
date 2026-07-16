"""WP6 — the matched physical-vs-proxy discrimination harness
(analysis.lateral_coupling_discrimination): determinism of the generated artifacts, full grid
coverage, the mirror/identical structural results, that the proxy exposes no physical pressure
observable, that alpha and Lambda are kept INDEPENDENT (no alpha=f(Lambda) mapping), and the
stale/regenerate contract of the generated-artifact check.
"""
import json

import pytest

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
    got = {(r["case_id"], r["lambda"]) for r in doc["rows"]}
    want = {(c.case_id, lam) for c in D.CASES for lam in D.LAMBDA_GRID}
    assert got == want
    assert len(doc["rows"]) == len(D.CASES) * len(D.LAMBDA_GRID)
    # boundary sweep around the provisional 0.05/5 labels is carried separately
    assert len(doc["boundary_rows"]) == len(D.CASES) * len(D.BOUNDARY_LAMBDAS)


def test_isoresistive_mirror_is_distinguishable_once_coupled():
    # equal end-to-end conductance (equal uncoupled outlet shares) yet distinguishable through
    # the total-flow / depthwise-transfer signature the share-only proxy cannot produce.
    rows = {r["lambda"]: r for r in D._build()["rows"] if r["case_id"] == "isoresistive_mirror"}
    assert rows[0.0]["mathematically_distinguishable"] is False   # uncoupled: identical
    for lam in (0.5, 1.0, 5.0):
        r = rows[lam]
        assert r["mathematically_distinguishable"] is True
        assert r["Q_over_Q0"] > 1.0                          # coupling raises total flow
        assert r["q_lat_1to2"] != 0.0                        # real transverse flux


def test_identical_paths_reports_no_lateral_effect():
    for r in [r for r in D._build()["rows"] if r["case_id"] == "identical_paths"]:
        assert r["q_lat_1to2"] == 0.0                        # negative control: never any flux
        assert r["mathematically_distinguishable"] is False
        assert r["pressure_gap_class"] == "not_applicable"   # gap0 == 0 -> N/A, not "0% reduction"


def test_proxy_exposes_no_physical_pressure_observable():
    # the discrimination is honest: physical-only observables are absent from the proxy, not 0
    p = D.frozen_two_path_proxy(D.P_IN, 3.0, 1.0, 1.0, 3.0, alpha=0.5)
    assert p["physical_observables_available"] is False
    assert all(v is None for v in p["physical_observables"].values())


def test_no_alpha_to_lambda_mapping():
    # the proxy takes alpha and never Lambda; the physical model takes G_lat (Lambda*g_ax) and
    # never alpha. They are searched independently over full grids -> no fitted correspondence.
    import inspect
    proxy_params = inspect.signature(D.frozen_two_path_proxy).parameters
    assert "alpha" in proxy_params and "Lambda" not in proxy_params and "G_lat" not in proxy_params
    phys_params = inspect.signature(D.lc.model1_two_path).parameters
    assert "G_lat" in phys_params and "alpha" not in phys_params
    # distinguishability is decided by grid search, not by any alpha=f(Lambda) closed form
    src = inspect.getsource(D.physical_row)
    assert "argmin" in src                                   # best alpha found by search


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
