"""Synthetic scalar checks; no observations, sources, fits or solver execution."""
from dataclasses import replace
from decimal import Decimal, FloatOperation, localcontext
import itertools
import json
import math
from pathlib import Path
import subprocess
import sys

import pytest

from examples.decision_resolution import (
    POLICY, QUALITY, bound, point, requirement, sensitivity, synthetic_cases,
)
from puckworks.validation.decision_resolution import (
    Basis, Counts, Interval, assess, conjunction, evaluate, interval_relation, point_relation,
)

D = Decimal


@pytest.mark.parametrize("op,lo,hi,expected", [
    ("<=", 3, 5, "satisfies"), ("<=", 6, 7, "violates"), ("<=", 4, 6, "overlaps"),
    ("<", 3, 4, "satisfies"), ("<", 5, 7, "violates"), ("<", 4, 5, "overlaps"),
    (">=", 5, 7, "satisfies"), (">=", 3, 4, "violates"), (">=", 4, 6, "overlaps"),
    (">", 6, 7, "satisfies"), (">", 3, 5, "violates"), (">", 5, 6, "overlaps"),
    ("<=", 5, 5, "satisfies"), ("<", 5, 5, "violates"),
    (">=", 5, 5, "satisfies"), (">", 5, 5, "violates"),
])
def test_interval_truth_table(op, lo, hi, expected):
    assert interval_relation(Interval(lo, hi), op, 5) == expected


@pytest.mark.parametrize("op,expected", [("<=", "violates"), ("<", "violates"),
                                         (">=", "satisfies"), (">", "satisfies")])
def test_near_boundary_no_tolerance_or_rounding(op, expected):
    above = math.nextafter(5.0, math.inf)
    assert point_relation(above, op, 5) == expected
    assert interval_relation(Interval(above, above), op, 5) == expected
    assert point_relation(D("5.000000000000000000000000000001"), op, D("5")) == expected
    below = math.nextafter(5.0, -math.inf)
    assert point_relation(below, op, 5) != expected


@pytest.mark.parametrize("value", [True, False, "1", None, complex(1), [1]])
def test_unsupported_numeric_inputs(value):
    with pytest.raises(TypeError):
        point_relation(value, "<=", 1)


@pytest.mark.parametrize("value", [float("nan"), float("inf"), -float("inf"), D("NaN"), D("sNaN"), D("Infinity")])
def test_nonfinite_values(value):
    with pytest.raises(ValueError):
        Interval(value, 1)
    with pytest.raises(ValueError):
        point_relation(1, "<=", value)


def test_invalid_bounds_operator_and_unspecified_basis():
    with pytest.raises(ValueError, match="inverted"):
        Interval(2, 1)
    with pytest.raises(ValueError, match="unsupported"):
        point_relation(1, "=", 1)
    with pytest.raises(ValueError, match="unsupported"):
        replace(requirement("r", "<=", "1"), decision_basis=None)


@pytest.mark.parametrize("value", [1, 1.0, D("1.000")])
def test_supported_numeric_representations_in_same_canonical_units(value):
    r = requirement("r", "<=", "1")
    e = replace(point(r, "1"), point=value)
    assert evaluate(r, e).contractual == "PASS"
    # The original representation is retained, including Decimal trailing zeros.
    encoded = assess((r,), {"r": e}, policy_version=POLICY).to_json()
    assert json.loads(encoded)["decisions"][0]["evidence"]["point"] == (
        {"decimal": "1.000"} if isinstance(value, Decimal) else value
    )


def test_mixed_decimal_float_comparison_is_independent_of_ambient_context():
    with localcontext() as context:
        context.traps[FloatOperation] = True
        context.prec = 2
        context.clear_flags()
        assert point_relation(D("0.1"), "<", 0.1) == "satisfies"
        assert interval_relation(Interval(D("0.1"), 0.1), ">=", D("0.1")) == "satisfies"
        assert not any(context.flags.values())


@pytest.mark.parametrize("name,contract,resolution", [
    ("A-upper-satisfies", "PASS", "PASS"), ("B-upper-violates", "FAIL", "FAIL"),
    ("C-upper-overlaps", "UNRESOLVED", "UNRESOLVED"),
    ("A-lower-satisfies", "PASS", "PASS"), ("B-lower-violates", "FAIL", "FAIL"),
    ("C-lower-overlaps", "UNRESOLVED", "UNRESOLVED"),
    ("E-bound", "PASS", "PASS"), ("E-sensitivity", "PASS", "UNRESOLVED"),
    ("F-stable-effect-precision-fails", "FAIL", "UNRESOLVED"),
    ("G-overlap-precision-fails", "FAIL", "UNRESOLVED"),
    ("H-adequate-insufficient-increment", "FAIL", "FAIL"),
    ("I-count-fails", "FAIL", "FAIL"), ("I-count-unresolved", "UNRESOLVED", "UNRESOLVED"),
    ("I-count-satisfied", "PASS", "PASS"), ("I-count-satisfied-incomplete", "PASS", "PASS"),
    ("I-separate-complete-support-fails", "FAIL", "FAIL"),
    ("I-adverse-diagnostic-not-a-gate", "PASS", "PASS"),
    ("J-contract-fail-resolution-overlap", "FAIL", "UNRESOLVED"),
    ("J-point-only-pass", "PASS", "UNRESOLVED"),
    ("K-full-scope-failure-incomplete", "FAIL", "FAIL"),
    ("K-incompatible-subset", "UNAVAILABLE", "UNAVAILABLE"),
    ("L-source-identity", "UNAVAILABLE", "UNAVAILABLE"),
    ("L-payload-integrity", "UNAVAILABLE", "UNAVAILABLE"),
])
def test_demonstration_matrix(name, contract, resolution):
    result = synthetic_cases()[name]
    assert (result.contractual, result.resolution) == (contract, resolution)


def test_precision_failure_is_separate_from_stability_and_integrity():
    for name, relation in (("F-stable-effect-precision-fails", "satisfies"),
                           ("G-overlap-precision-fails", "overlaps")):
        result = synthetic_cases()[name]
        precision, effect = result.decisions
        assert precision.requirement.role == "precision"
        assert precision.contractual == "FAIL"
        assert effect.range_relation == relation
        assert "Tested-sensitivity" in effect.interpretation
        assert not result.reliance_blocked
        assert result.failed_controlling == ("precision",)


def test_adequacy_increment_and_unapproved_practical_basis_remain_distinct():
    result = synthetic_cases()["H-adequate-insufficient-increment"]
    adequacy, increment = result.decisions
    assert adequacy.resolution == "PASS"
    assert increment.resolution == "FAIL"
    assert increment.requirement.comparator == "SYNTHETIC-CONTROL"
    assert result.failed_controlling == ("increment",)
    r = requirement("gain", ">=", "0.1", role="increment")
    d = evaluate(r, bound(r, "1", "0.9", "1.1"))
    assert d.contractual == d.resolution == "PASS"
    assert any("no practical-value/adoption" in text for text in d.limitations)


def test_point_contract_preserved_and_bound_contract_requires_bound():
    r = requirement("r", "<=", "10")
    assert evaluate(r, bound(r, "11", "9", "12")).contractual == "FAIL"
    only = point(r, "9")
    d = evaluate(r, only)
    assert d.point_relation == "satisfies" and d.range_relation is None
    assert d.resolution == "UNRESOLVED" and "measurement" in d.evidence.unknown_components
    assert evaluate(replace(r, decision_basis="applicable_bound"), only).contractual == "UNAVAILABLE"
    assert evaluate(replace(r, decision_basis="applicable_bound"), sensitivity(r, "9", "8", "9")).contractual == "UNAVAILABLE"


def test_same_endpoints_not_same_claim_and_label_alone_cannot_upgrade():
    r = requirement("r", ">=", "0.1")
    a, b = bound(r, "2", "1.97", "2.03"), sensitivity(r, "2", "1.97", "2.03")
    assert evaluate(r, a).range_relation == evaluate(r, b).range_relation == "satisfies"
    assert evaluate(r, a).resolution == "PASS" and evaluate(r, b).resolution == "UNRESOLVED"
    with pytest.raises(ValueError, match="bound requires"):
        replace(b, kind="bound")
    with pytest.raises(ValueError, match="tested sensitivities"):
        replace(b.basis, kind="analytic")


@pytest.mark.parametrize("field,value", [
    ("units", "g"), ("observable", "another observable"), ("aggregation", "pooled fraction mean"),
    ("estimand", "population mean"), ("information", "target-informed"), ("domain", "another domain"),
    ("support", (("SYNTHETIC-other", "SYNTHETIC-other"),)),
])
def test_scope_and_basis_mismatches_never_support_conclusion(field, value):
    r = requirement("r", "<=", "5")
    e = bound(r, "1", "0", "2")
    mismatched = replace(e.basis.scope, **{field: value})
    result = evaluate(r, replace(e, basis=replace(e.basis, scope=mismatched)))
    assert result.contractual == result.resolution == "UNAVAILABLE"
    assert result.point_relation == "satisfies" and result.reliance_blocked
    assert "Diagnostic arithmetic only" in result.interpretation


def test_numerical_basis_not_total_uncertainty_and_allowance_is_conditional():
    r = requirement("r", "<=", "5", decision_basis="applicable_bound")
    e = bound(r, "1", "0", "2")
    numeric = replace(e, basis=replace(e.basis, kind="numerical", components=("reduction",)))
    assert evaluate(r, numeric).contractual == "UNAVAILABLE"
    total = replace(r, resolution_components=("reduction", "measurement", "training"))
    assert evaluate(total, numeric).resolution == "UNRESOLVED"
    allowance = replace(e, basis=replace(e.basis, kind="allowance"))
    assert evaluate(r, allowance).resolution == "PASS"
    assert "Allowance-conditional" in evaluate(r, allowance).interpretation


def test_incomplete_support_and_full_scope_failure_witness():
    result = synthetic_cases()["K-full-scope-failure-incomplete"]
    d = result.decisions[0]
    assert not result.support_complete and not result.assessment_complete
    assert result.resolved_failure_witnesses == ("full-metric",)
    e = replace(d.evidence, basis=replace(d.evidence.basis, full_support_justification=None))
    assert evaluate(d.requirement, e).resolution == "UNRESOLVED"
    # A valid failure witness survives an unavailable, separately required component.
    extra = requirement("unavailable", "<=", "10")
    a = assess((d.requirement, extra), {d.requirement.identity: d.evidence}, policy_version=POLICY)
    assert a.resolution == "FAIL" and not a.assessment_complete and len(a.decisions) == 2


@pytest.mark.parametrize("field", ["admissible", "source_identity", "payload_integrity", "numerical_integrity"])
@pytest.mark.parametrize("factory", [bound, sensitivity])
def test_integrity_rejection_overrides_large_margin_but_keeps_diagnostic_arithmetic(field, factory):
    r = requirement("r", ">=", "0.1")
    e = replace(factory(r, "20", "19", "21"), quality=replace(QUALITY, **{field: False}))
    result = assess((r,), {"r": e}, policy_version=POLICY)
    assert result.resolution == result.contractual == "UNAVAILABLE"
    assert result.reliance_blocked and not result.assessment_complete
    assert result.decisions[0].range_relation == "satisfies"
    assert "stable" not in result.decisions[0].interpretation.lower()


@pytest.mark.parametrize("N,definite,possible,members", [
    (True, 0, 0, ()), (1, True, 1, (("a", "definite"),)),
    (1, 1, False, (("a", "definite"),)), (0, 0, 0, ()),
    (1, 2, 1, (("a", "definite"),)), (1, 0, 2, (("a", "possible"),)),
    (2, 1, 1, (("a", "definite"), ("b", "missing"))),
    (2, 1, 2, (("a", "definite"), ("a", "possible"))),
    (2, 2, 2, (("a", "definite"),)),
])
def test_inconsistent_count_accounting_rejected(N, definite, possible, members):
    with pytest.raises(ValueError):
        Counts(N, definite, possible, members, "applicable_bound", "synthetic definition")


def test_mutable_count_members_rejected():
    with pytest.raises(ValueError, match="immutable two-item"):
        Counts(1, 1, 1, (["a", "definite"],), "applicable_bound", "Synthetic bound satisfaction")


@pytest.mark.parametrize("case,relation", [("I-count-satisfied", "satisfies"), ("I-count-fails", "violates")])
def test_incompatible_bound_count_cannot_decide_contract(case, relation):
    d = synthetic_cases()[case].decisions[1]
    r = replace(d.requirement, resolution_components=("measurement",))
    e = replace(d.evidence, basis=replace(d.evidence.basis, kind="numerical", components=("reduction",)))
    result = evaluate(r, e)
    assert result.contractual == "UNAVAILABLE" and result.resolution == "UNRESOLVED"
    assert result.count_relation == relation and not result.assessment_complete


@pytest.mark.parametrize("role", ["count", "coverage"])
@pytest.mark.parametrize("basis", ["point", "applicable_bound"])
def test_count_and_coverage_cannot_bypass_member_accounting_via_scalar_basis(role, basis):
    r = requirement("r", ">=", "6.1")
    with pytest.raises(ValueError, match="role requires explicit"):
        replace(r, role=role, decision_basis=basis)


@pytest.mark.parametrize("k", [True, -1, 9, 6.0])
def test_invalid_required_count_rejected(k):
    d = synthetic_cases()["I-count-satisfied"].decisions[1]
    assert d.requirement.identity == "count"
    with pytest.raises((TypeError, ValueError)):
        replace(d.requirement, threshold=k)


def test_count_interpretations_and_completeness_do_not_promote_claims():
    a = synthetic_cases()["I-count-satisfied-incomplete"]
    assert a.resolution == "PASS" and not a.assessment_complete and not a.support_complete
    d = a.decisions[1]
    for meaning in ("point_contract", "tested_sensitivities"):
        basis = (replace(d.evidence.basis, kind="descriptive", components=()) if meaning == "point_contract"
                 else Basis("sensitivity", d.requirement.scope, "Finite synthetic perturbations.", (), (), ("trial",)))
        e = replace(d.evidence, counts=replace(d.evidence.counts, meaning=meaning), basis=basis)
        r = replace(d.requirement, count_meaning=meaning)
        assert evaluate(r, e).contractual == "PASS" and evaluate(r, e).resolution == "UNRESOLVED"
        with pytest.raises(ValueError, match="matching explicit"):
            evaluate(d.requirement, e)


@pytest.mark.parametrize("op", ["<=", "<", ">=", ">"])
def test_widening_cannot_create_resolution(op):
    r = requirement("r", op, "5", decision_basis="applicable_bound")
    for lo, hi in ((3, 4), (4, 6), (6, 7), (5, 5)):
        original = bound(r, "5", str(lo), str(hi))
        old = evaluate(r, original).resolution
        for delta in (1, 3):
            # Point, scope, basis and requirement all remain fixed.
            enlarged = replace(original, interval=Interval(lo - delta, hi + delta))
            new = evaluate(r, enlarged).resolution
            assert new not in ("PASS", "FAIL") or new == old


def test_weakening_evidence_or_removing_support_never_strengthens():
    r = requirement("r", "<=", "5", decision_basis="applicable_bound")
    e = bound(r, "4", "3", "6")
    assert evaluate(r, e).resolution == "UNRESOLVED"
    assert evaluate(r, replace(e, observed_support=())).resolution != "PASS"
    for weaker in (sensitivity(r, "4", "3", "6"), point(r, "4"), None):
        assert evaluate(r, weaker).resolution not in ("PASS", "FAIL")


def test_diagnostics_and_permutation_do_not_change_controlling_outcomes():
    good = requirement("required", "<=", "5", decision_basis="applicable_bound")
    diagnostic = replace(good, identity="diagnostic", controlling=False)
    es = {"required": bound(good, "4", "3", "4"), "diagnostic": bound(diagnostic, "9", "8", "10")}
    outputs = [assess(order, es, policy_version=POLICY).to_json() for order in itertools.permutations((good, diagnostic))]
    assert outputs[0] == outputs[1]
    assert json.loads(outputs[0])["contractual"] == "PASS"
    blocked = replace(es["diagnostic"], quality=replace(QUALITY, admissible=False))
    a = assess((good, diagnostic), {**es, "diagnostic": blocked}, policy_version=POLICY)
    assert a.resolution == "PASS" and not a.reliance_blocked


def test_empty_duplicate_missing_and_undeclared_components():
    r = requirement("r", "<=", "1")
    for reqs, es in (((), {}), ((r, r), {}), ((replace(r, controlling=False),), {}), ((r,), {"other": point(r, "0")})):
        with pytest.raises(ValueError):
            assess(reqs, es, policy_version=POLICY)
    missing = assess((r,), {}, policy_version=POLICY)
    assert missing.contractual == missing.resolution == "UNAVAILABLE"
    assert len(missing.decisions) == 1 and not missing.assessment_complete
    assert conjunction(()) == "UNAVAILABLE"


@pytest.mark.parametrize("operation", ["equivalence", "confidence_interval", "bootstrap", "population_reliability", "adoption"])
def test_unsupported_inference_equivalence_and_adoption(operation):
    r = requirement("r", "<=", "1")
    with pytest.raises(ValueError, match="unsupported request"):
        assess((r,), {"r": point(r, "0")}, policy_version=POLICY, request=operation)


def test_software_gate_success_is_not_scientific_resolution():
    from puckworks.gate_runner import GateResult, GateStatus, GateSuiteResult
    for status in (GateStatus.PASS, GateStatus.SKIP):
        assert GateSuiteResult([GateResult("synthetic", "software", status)]).passed
        r = requirement("science", "<=", "5")
        assert evaluate(r, None).resolution == "UNAVAILABLE"
        assert evaluate(r, point(r, "1")).resolution == "UNRESOLVED"


def test_import_and_evaluation_do_not_access_sources_or_execute_producers(tmp_path):
    # Standard Python import reads module bytecode/source. Block data and producer
    # access after package bootstrap, preserving the existing package initializer.
    script = '''
import builtins, importlib, pathlib, socket, subprocess, sys
import puckworks
def forbidden(*args, **kwargs):
    raise AssertionError("unexpected side effect")
builtins.open = forbidden
pathlib.Path.open = forbidden
socket.socket.connect = forbidden
subprocess.Popen = forbidden
class Block:
    def find_spec(self, fullname, *args):
        if fullname.startswith(("puckworks.analysis", "puckworks.data", "puckworks.models", "scipy.optimize")):
            raise AssertionError("producer/source import: " + fullname)
sys.meta_path.insert(0, Block())
from puckworks.validation.decision_resolution import Interval, interval_relation
assert interval_relation(Interval(1, 2), "<=", 3) == "satisfies"
'''
    subprocess.run([sys.executable, "-B", "-c", script], check=True, capture_output=True)


def test_example_deterministic_output_and_only_requested_write(tmp_path):
    command = [sys.executable, "-B", "-m", "examples.decision_resolution"]
    first = subprocess.run(command, check=True, capture_output=True, text=True).stdout
    second = subprocess.run(command, check=True, capture_output=True, text=True).stdout
    assert first == second
    target = tmp_path / "synthetic.json"
    written = subprocess.run(command + ["--output", str(target)], check=True, capture_output=True, text=True)
    assert written.stdout == "" and target.read_text() == first
    assert list(tmp_path.iterdir()) == [target]
    assert subprocess.run(command + ["--output", str(target)], capture_output=True).returncode != 0
    report = json.loads(first)
    assert report["classification"] == "SYNTHETIC_VERIFICATION_ONLY"
    assert list(report["cases"]) == sorted(report["cases"])
    assert all("timestamp" not in case and "environment" not in case for case in report["cases"].values())
    source = Path("puckworks/validation/decision_resolution.py").read_text()
    assert "puckworks.analysis" not in source and "puckworks.data" not in source
