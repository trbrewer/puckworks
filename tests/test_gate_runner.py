"""P0.2 — typed, non-short-circuiting gate evaluation.

Fast tests use synthetic components; the real-registry suite is marked slow.
"""
from types import SimpleNamespace

from puckworks.gate_runner import (
    GateStatus, evaluate_gate, evaluate_component_gates, evaluate_all_gates)


def _g_pass():
    return dict(passed=True, x=1)


def _g_fail():
    return dict(passed=False, why="nope")


def _g_fail2():
    return dict(passed=False, why="also nope")


def _g_raise():
    raise ValueError("boom")


def _g_badtype():
    return 42


def _g_nopassed():
    return dict(x=1)


def _comp(name, gates):
    return SimpleNamespace(name=name, gates=gates)


def test_all_failures_are_reported_not_short_circuited():
    comps = [_comp("a", [_g_fail]), _comp("b", [_g_fail2]), _comp("c", [_g_pass])]
    suite = evaluate_all_gates(components=comps)
    fails = [r for r in suite.results if r.status == GateStatus.FAIL]
    assert len(fails) == 2                                    # BOTH failures reported
    assert {r.component_id for r in fails} == {"a", "b"}
    assert any(r.status == GateStatus.PASS for r in suite.results)   # later gate still ran
    assert suite.passed is False


def test_failure_does_not_prevent_later_gates_in_same_component():
    c = _comp("x", [_g_fail, _g_pass])
    results = evaluate_component_gates("x", c)
    assert {r.status for r in results} == {GateStatus.FAIL, GateStatus.PASS}


def test_exception_becomes_error_and_later_gates_still_run():
    c = _comp("x", [_g_raise, _g_pass])
    results = evaluate_component_gates("x", c)
    statuses = {r.gate_id: r.status for r in results}
    assert statuses["_g_raise"] == GateStatus.ERROR
    assert statuses["_g_pass"] == GateStatus.PASS
    err = next(r for r in results if r.status == GateStatus.ERROR)
    assert err.exception_type == "ValueError" and "boom" in err.exception_message


def test_invalid_return_types_are_errors_not_silent_pass():
    assert evaluate_gate("c", _g_badtype).status == GateStatus.ERROR       # non-mapping
    assert evaluate_gate("c", _g_nopassed).status == GateStatus.ERROR      # no 'passed'


def test_non_boolean_passed_is_error_not_coerced():
    # PW-GATE-001: bool("false")/bool("0")/bool(1) would silently PASS; must ERROR.
    import numpy as np
    for bad in ("false", "0", "", "true", 1, 0, 1.0, None, [], {}):
        assert evaluate_gate("c", (lambda b=bad: dict(passed=b))).status == GateStatus.ERROR, bad
    # real booleans (Python + numpy) still classify correctly
    assert evaluate_gate("c", lambda: dict(passed=True)).status == GateStatus.PASS
    assert evaluate_gate("c", lambda: dict(passed=False)).status == GateStatus.FAIL
    assert evaluate_gate("c", lambda: dict(passed=np.True_)).status == GateStatus.PASS
    assert evaluate_gate("c", lambda: dict(passed=np.False_)).status == GateStatus.FAIL


def test_zero_gate_component_is_explicit_skip_not_pass():
    r = evaluate_component_gates("nogate", _comp("nogate", []))
    assert len(r) == 1 and r[0].status == GateStatus.SKIP
    assert r[0].status != GateStatus.PASS                    # never a vacuous pass


def test_acknowledged_zero_gate_exception():
    # lb_taichi is a registered zero-gate component recorded in the evidence policy
    r = evaluate_component_gates("brewer2026.lb_taichi")
    assert len(r) == 1 and r[0].status == GateStatus.ACKNOWLEDGED_EXCEPTION


def test_boolean_wrapper_false_on_fail_or_error(monkeypatch):
    from puckworks import registry as R
    monkeypatch.setattr(R, "get", lambda n: _comp(n, [_g_fail]))
    assert R.run_gates("x", verbose=False) is False
    monkeypatch.setattr(R, "get", lambda n: _comp(n, [_g_raise]))
    assert R.run_gates("x", verbose=False) is False
    monkeypatch.setattr(R, "get", lambda n: _comp(n, [_g_pass]))
    assert R.run_gates("x", verbose=False) is True


def test_deterministic_ordering():
    c = _comp("x", [_g_raise, _g_pass, _g_fail])              # unsorted input
    ids = [r.gate_id for r in evaluate_component_gates("x", c)]
    assert ids == sorted(["_g_raise", "_g_pass", "_g_fail"])  # sorted by gate name


def test_json_report_conforms_to_versioned_schema():
    comps = [_comp("a", [_g_pass, _g_fail]), _comp("z", [])]
    d = evaluate_all_gates(components=comps).to_dict(include_runtime=False)
    assert d["schema_version"] == 1
    assert set(d) >= {"schema_version", "passed", "counts_by_status", "results"}
    for r in d["results"]:
        assert set(r) >= {"component_id", "gate_id", "status", "metrics", "schema_version"}
        assert r["status"] in {s.value for s in GateStatus}
    # deterministic: two calls produce identical structural output
    assert evaluate_all_gates(components=comps).to_dict(include_runtime=False) == d


def test_real_registry_suite_passes():   # auto-marked slow via conftest.SLOW (runs the full suite)
    suite = evaluate_all_gates()
    assert suite.passed, suite.summary_text()
    c = suite.counts_by_status
    assert c["FAIL"] == 0 and c["ERROR"] == 0
    assert c["ACKNOWLEDGED_EXCEPTION"] >= 1                   # lb_taichi
