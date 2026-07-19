"""Native reference runner authority + validation + selection (PV-19B Phase 4, #70).

Offline + deterministic. Guards that every pass/band verdict a runner reports is the AUTHORITATIVE gate
verdict (no duplicated literal that can drift), that the foster first-drip crossing is explicit (no false
argmax-of-all-False crossing at t[0]), that RunnerSpec + the runner registry are validated, that a result
is schema-sanitized + finite, and that selection rejects an unknown id (never a silent drop).
"""
import numpy as np
import pytest

from puckworks.product import lab_runners as lr
from puckworks.validation import gates as G


# ── gate is the single authority for every pass/band verdict ────────────────────────
@pytest.mark.parametrize("cid,gate_name", [
    ("waszkiewicz2025.poroelastic", "gate_waszkiewicz_static_refit"),
    ("wadsworth2026.permeability", "gate_wadsworth_collapse"),
    ("foster2025.infiltration", "gate_infiltration_triangle"),
])
def test_runner_verdict_is_the_authoritative_gate_verdict(cid, gate_name):
    r = lr.execute_runner(cid)
    assert r["status"] == "executed"
    assert r["gate_authority"]["gate"] == gate_name
    # the runner surfaces the gate's own verdict verbatim (coerced to plain JSON types)
    assert r["gate_authority"]["verdict"]["passed"] == bool(getattr(G, gate_name)()["passed"])
    # and the derived boolean output tracks the gate, not a re-derived literal
    derived = {o["name"]: o["value"] for o in r["outputs"] if o["role"] == "derived"}
    assert any(v == r["gate_authority"]["verdict"]["passed"] for v in derived.values())


def test_wadsworth_band_literal_is_not_recomputed_in_the_runner():
    # the 0.7 < ratio < 1.2 band lives in the gate; the runner must not re-evaluate it as executable code
    import ast
    src = open(lr.__file__).read()
    tree = ast.parse(src)
    # no numeric Compare against 1.2 / 0.7 anywhere in runner code (docstrings/strings are fine)
    bad = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Compare):
            for c in [node.left, *node.comparators]:
                if isinstance(c, ast.Constant) and c.value in (0.7, 1.2):
                    bad.append(node.lineno)
    assert not bad, f"runner re-derives the gate band as code at lines {bad}"


# ── no invented first-drip crossing ─────────────────────────────────────────────────
def test_first_crossing_returns_none_when_never_crossed():
    t = np.array([0.0, 1.0, 2.0, 3.0])
    w = np.array([0.0, 0.1, 0.2, 0.3])                 # never exceeds 0.5 g
    assert lr._first_crossing_time(t, w, 0.5) is None   # NOT t[0]=0.0


def test_first_crossing_returns_the_first_true_sample():
    t = np.array([0.0, 1.0, 2.0, 3.0])
    w = np.array([0.0, 0.0, 0.6, 0.7])
    assert lr._first_crossing_time(t, w, 0.5) == 2.0


def test_foster_runner_never_reports_a_zero_first_drip_when_absent(monkeypatch):
    # force a no-crossing weight trace; the observed first drip must be unavailable, never 0.0
    from puckworks.product import lab_reference_producers as P
    real = dict(P._data_fixture("de1_fixtureA.json"))
    real["weight_g"] = [0.0] * len(real["weight_g"])   # never crosses the threshold
    monkeypatch.setattr(P, "_data_fixture", lambda name: real)
    r = lr.execute_runner("foster2025.infiltration")
    obs = {o["name"]: o for o in r["outputs"]}["observed_first_drip_s"]
    assert obs["status"] == "unavailable" and obs["value"] is None
    within = {o["name"]: o for o in r["outputs"]}["observation_within_bracket_runner"]
    assert within["value"] is None                     # not computed as a false crossing


# ── RunnerSpec + registry validation ────────────────────────────────────────────────
def test_runner_spec_rejects_invalid_runtime_class():
    with pytest.raises(ValueError):
        lr.RunnerSpec("x", "1", "c", "not-a-class")
    with pytest.raises(ValueError):
        lr.RunnerSpec("", "1", "c", "interactive-fast")


def test_validate_runners_is_clean_and_catches_a_bad_spec(monkeypatch):
    assert lr.validate_runners() == []
    bad = dict(lr.RUNNERS)
    bad["mislabelled.key"] = (lr.RunnerSpec("z", "1", "other.component", "interactive-fast"), lambda: {})
    monkeypatch.setattr(lr, "RUNNERS", bad)
    problems = lr.validate_runners()
    assert any("!= spec.component_id" in p or "unregistered" in p for p in problems)


# ── sanitized result schema (finite; units + roles) ─────────────────────────────────
def test_non_finite_output_becomes_failed_not_a_nan_result(monkeypatch):
    spec, _ = lr.RUNNERS["wadsworth2026.permeability"]
    monkeypatch.setitem(lr.RUNNERS, "wadsworth2026.permeability",
                        (spec, lambda: {"native_inputs": [{"name": "x"}],
                                        "outputs": [{"name": "y", "value": float("nan"), "unit": "-",
                                                     "role": "derived"}]}))
    r = lr.execute_runner("wadsworth2026.permeability")
    assert r["status"] == "FAILED" and "non-finite" in r["error"].lower()


def test_output_missing_unit_or_role_becomes_failed(monkeypatch):
    spec, _ = lr.RUNNERS["wadsworth2026.permeability"]
    monkeypatch.setitem(lr.RUNNERS, "wadsworth2026.permeability",
                        (spec, lambda: {"native_inputs": [], "outputs": [{"name": "y", "value": 1.0}]}))
    r = lr.execute_runner("wadsworth2026.permeability")
    assert r["status"] == "FAILED" and "unit/role" in r["error"]


# ── selection API ───────────────────────────────────────────────────────────────────
def test_selection_rejects_unknown_id_by_default():
    with pytest.raises(ValueError):
        lr.run_selected(["waszkiewicz2025.poroelastic", "not.a.runner"])
    with pytest.raises(KeyError):
        lr.execute_runner("not.a.runner")


def test_selection_best_effort_mode_skips_unknown_without_raising():
    out = lr.run_selected(["waszkiewicz2025.poroelastic", "not.a.runner"], strict=False)
    assert [r["component_id"] for r in out] == ["waszkiewicz2025.poroelastic"]


def test_available_runners_and_runtime_class():
    assert lr.available_runners() == sorted(lr.RUNNERS)
    for cid in lr.available_runners():
        assert lr.runtime_class(cid) in lr.RUNTIME_CLASSES
