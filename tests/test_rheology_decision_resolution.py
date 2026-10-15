"""Synthetic case-adapter tests; no retained numerical results or EWP execution."""
import ast
import copy
import hashlib
import json
from pathlib import Path
import sys

import pytest

from puckworks.analysis import rheology_decision_resolution as case

FIXTURE = json.loads((Path(__file__).parent / "fixtures/rheology_decision_resolution_boundaries.json").read_text())
MANIFEST = json.loads((case.BUNDLE / "INPUT_MANIFEST.json").read_text())


def number(value):
    if isinstance(value, dict):
        if "binary64_hex" in value:
            return float.fromhex(value["binary64_hex"])
        return float(value["special"])
    return value


@pytest.mark.parametrize("fixture", FIXTURE["cases"], ids=lambda f: f["id"])
def test_independent_boundaries(fixture):
    source = {k: number(v) for k, v in fixture["input"].items()}
    result = case.scalar(source["question"], source["M"], source["u"], source["b"],
                         complete=source["evidence_complete"])
    for field, expected in fixture["expected"].items():
        assert result[field] == expected


@pytest.mark.parametrize("fixture", FIXTURE["aggregate_cases"], ids=lambda f: f["id"])
def test_independent_failure_precedence(fixture):
    flags = [label for label, count in fixture["decision_counts"].items() for _ in range(count)]
    assert len(flags) == fixture["expected_total"]
    assert case.primary_aggregate(flags) == fixture["expected"]


def synthetic_inputs():
    # Explicit synthetic zero discrepancies, zero sensitivities. No case output
    # supplies expectations; fixed identities/units/budgets come from the protocol.
    data = {"primary": {}, "secondary": {},
            "disposition": "E2_CONDUCTANCE_MATCHED_REVERSAL_SUFFICIENT_FOR_TESTED_OUTPUTS"}
    coverage = {}
    budgets = {"E_Qint": .01, "E_Qpeak": .02, "D_share_mean_pp": 1.,
               "D_share_peak_pp": 2., "E_Spath": .01, "D_TDS_pp": .1}
    for spec in MANIFEST["population"]:
        group, name, metric = spec["id"].split("/")
        block = data[group].setdefault(name, {"variants": {}, "arithmetic": {}, "decisions": {}})
        terms = {"time": 0., "axial": 0., "property": 0., "arithmetic": 0.,
                 "Cradial" if group == "primary" else "both_C_radial": 0.}
        block["decisions"][metric] = dict(value=0., u_total=0., budget=budgets[metric],
            terms=terms, units="fraction" if metric.startswith("E_") else "percentage_points",
            evidence_complete=True, decision="PASS" if group == "primary" else "BELOW_DECLARED_MATERIALITY_BUDGET")
        for variant in spec["variant_pointers"]:
            block["variants"].setdefault(variant, {"delivery_status": "VALID"})[metric] = 0.
            block["arithmetic"].setdefault(variant, {})[metric] = 0.
        end = .015983191 if spec["history"] == "UP" else .016114389
        for locator in spec["coverage_pointers"]:
            coverage[locator[1:]] = dict(B_star_kg=end, terminal_beverage_kg=2*end,
                                        reaches_support=True, scored_fraction_of_terminal=.5)
    return data, coverage


def selected(group="primary", metric="D_TDS_pp"):
    return next(s for s in MANIFEST["population"] if s["group"] == group and s["metric"] == metric)


@pytest.mark.parametrize("fixture", FIXTURE["invalid_cases"], ids=lambda f: f["id"])
def test_independently_specified_invalid_inputs(fixture):
    values = copy.deepcopy(FIXTURE["invalid_case_base"])
    values.update({k: number(v) if k != "terms" else v for k, v in fixture.get("replace", {}).items()})
    if "remove" in fixture:
        values.pop(fixture["remove"])
    issues = case.check_terms(values["question"], values["terms"], values.get("u"))
    compatible = (values["metric_units"] == values["allowance_units"]
                  and values["declared_B_star"] == values["imported_B_star"])
    result = case.scalar(values["question"], values.get("M"), values.get("u"), values["b"],
                         complete=values["evidence_complete"] and compatible and not issues)
    assert result["historical_decision"] == "UNRESOLVED"
    assert result["envelope_relation"] == "UNAVAILABLE"


@pytest.mark.parametrize("mutation", ["unit", "budget", "negative", "nan", "missing_term", "sum",
    "variant", "arithmetic", "missing_variant", "short_support", "missing_coverage", "delivery_status"])
def test_real_adapter_rejects_bad_synthetic_row(mutation):
    data, coverage = synthetic_inputs()
    spec = selected()
    _, name, metric = spec["id"].split("/")
    block = data["primary"][name]
    row = block["decisions"][metric]
    if mutation == "unit":
        row["units"] = "fraction"
    elif mutation == "budget":
        row["budget"] = .2
    elif mutation == "negative":
        row["terms"]["time"] = -1.
    elif mutation == "nan":
        row["value"] = float("nan")
    elif mutation == "missing_term":
        del row["terms"]["arithmetic"]
    elif mutation == "sum":
        row["u_total"] = 1e-20
    elif mutation == "variant":
        block["variants"]["temporal"][metric] = .001
    elif mutation == "arithmetic":
        block["arithmetic"]["base"][metric] = 1e-20
    elif mutation == "missing_variant":
        del block["variants"]["radial"]
    elif mutation == "short_support":
        coverage[spec["coverage_pointers"][0][1:]]["B_star_kg"] *= .5
    elif mutation == "missing_coverage":
        del coverage[spec["coverage_pointers"][0][1:]]
    elif mutation == "delivery_status":
        block["variants"]["base"]["delivery_status"] = "INSUFFICIENT_SUPPORT"
    result = case.evaluate_row(spec, data, coverage, [])
    assert result["issues"]
    assert result["reproduced_historical_decision"] == "UNRESOLVED"
    assert result["envelope_relation"] == "UNAVAILABLE"
    assert result["helper"] is None


def test_complete_population_and_determinism():
    data, coverage = synthetic_inputs()
    result = case.evaluate_population(MANIFEST, data, coverage, [])
    assert len(result["cases"]) == 32
    assert result["summary"]["primary"]["reproduced"] == {"PASS": 24}
    assert result["summary"]["secondary"]["reproduced"] == {"BELOW_DECLARED_MATERIALITY_BUDGET": 8}
    assert len({r["id"] for r in result["cases"]}) == 32
    assert [r["id"] for r in result["cases"]] == sorted(r["id"] for r in result["cases"])
    reversed_data = dict(reversed(list(data.items())))
    assert case.dumps(result) == case.dumps(case.evaluate_population(MANIFEST, reversed_data, coverage, []))
    for r in result["cases"]:
        assert r["helper"]["bound_resolution"] == "UNRESOLVED"
        assert r["helper"]["contractual"] == "UNAVAILABLE"
        assert r["helper"]["evidence_kind"] == r["helper"]["basis_kind"] == "sensitivity"
        assert r["unknown_uncertainty_components"]


def test_missing_decision_retained_and_siblings_counted():
    data, coverage = synthetic_inputs()
    spec = selected()
    del data["primary"][spec["id"].split("/")[1]]["decisions"][spec["metric"]]
    result = case.evaluate_population(MANIFEST, data, coverage, [])
    assert result["missing_decisions"] == [spec["id"]]
    assert len(result["cases"]) == 32
    assert result["summary"]["primary"]["reproduced"] == {"PASS": 23, "UNRESOLVED": 1}
    assert result["reproduced_primary_aggregate"] == "E2_CONDUCTANCE_MATCHED_REVERSAL_UNRESOLVED"


@pytest.mark.parametrize("mutation", ["duplicate", "missing", "extra"])
def test_population_integrity(mutation):
    manifest = copy.deepcopy(MANIFEST)
    data, coverage = synthetic_inputs()
    if mutation == "duplicate":
        manifest["population"][-1] = manifest["population"][0]
    elif mutation == "missing":
        manifest["population"].pop()
    else:
        data["primary"]["EXTRA"] = {"decisions": {"E_Spath": {}}}
    with pytest.raises(ValueError):
        case.evaluate_population(manifest, data, coverage, [])


def test_json_rejects_duplicates_nonfinite_and_serialization(tmp_path):
    p = tmp_path / "input.json"
    for text in ('{"x":1,"x":2}', '{"x":NaN}', '{"x":Infinity}'):
        p.write_text(text)
        with pytest.raises(ValueError):
            case.load_json(p)
    with pytest.raises(ValueError):
        case.dumps({"x": float("inf")})


def test_historical_sum_preserves_compensation():
    # Exact real sum is 1e16+2; naive pre-3.12 sum loses both unit increments.
    assert case.historical_sum([1e16, 1., 1., 0., 0.]) == 10000000000000002.
    assert case.check_terms("primary", {"time":1e16, "axial":1., "Cradial":1.,
                                        "property":0., "arithmetic":0.}, 10000000000000002.) == []


def test_radial_construction_and_scored_support_are_distinct():
    data, coverage = synthetic_inputs()
    for group, wrong, right in (("primary", "both_C_radial", "Cradial"),
                               ("secondary", "Cradial", "both_C_radial")):
        spec = selected(group)
        expected_radial = "C refined; E2 fixed at base" if group == "primary" else "BOTH C configurations refined"
        row = case.evaluate_row(spec, data, coverage, [])
        assert row["refinement_construction"]["radial"] == expected_radial
        assert row["support"]["B_star_kg"] == "0.016114389"
        inputs = data[group][spec["id"].split("/")[1]]["decisions"][spec["metric"]]
        inputs["terms"][wrong] = inputs["terms"].pop(right)
        assert case.evaluate_row(spec, data, coverage, [])["envelope_relation"] == "UNAVAILABLE"


def test_missing_delivery_support_does_not_erase_hydraulic_decisions():
    data, coverage = synthetic_inputs()
    result = case.evaluate_population(MANIFEST, data, {}, ["missing support"])
    assert result["summary"]["primary"]["reproduced"] == {"PASS": 16, "UNRESOLVED": 8}
    assert result["summary"]["secondary"]["reproduced"] == {"UNRESOLVED": 8}


def test_helper_equality_does_not_overwrite_contract_and_precision_is_separate():
    spec = selected()
    for magnitude, allowance, relation in ((12., 2., "violates"), (13., 3., "violates")):
        result = case.scalar("primary", magnitude, allowance, 10.)
        helper = case.helper_diagnostic(spec, result, magnitude, 10.)
        assert result["historical_decision"] == "UNRESOLVED"
        assert helper["range_relation"] == relation
        assert helper["bound_resolution"] == "UNRESOLVED"
    result = case.scalar("secondary", 13., float.fromhex("0x1.0000000000001p+1"), 10.)
    helper = case.helper_diagnostic(selected("secondary"), result, 13., 10.)
    assert helper["range_relation"] == "satisfies"
    assert helper["bound_resolution"] == "UNRESOLVED"
    assert result["precision_state"] == "NOT_MET"
    assert result["historical_decision"] == "UNRESOLVED"


def test_source_authentication_is_read_only_and_hash_bound(tmp_path, monkeypatch):
    root = tmp_path / "ewp"
    folder = root / "docs/analysis/sci_md_rheology_010"
    folder.mkdir(parents=True)
    names = ("METRICS", "COVERAGE", "SUPPORT", "SUPPORT_RECEIPT", "QUALIFICATION", "REFERENCE_QUALIFICATION")
    for name in names:
        (folder / (name + ".json")).write_text('{}\n')
    manifest = {"evidence": {"commit":"synthetic", "files":[
        {"path":str(p.relative_to(root)), "sha256":hashlib.sha256(p.read_bytes()).hexdigest()}
        for p in folder.iterdir()]}, "policy":{"files":[]}}
    calls = []
    def git_read(args, **kwargs):
        calls.append(args)
        assert args == ["git", "-C", str(root), "rev-parse", "HEAD"]
        assert kwargs["env"]["GIT_OPTIONAL_LOCKS"] == "0"
        return "synthetic\n"
    monkeypatch.setattr(case.subprocess, "check_output", git_read)
    before = {p: p.read_bytes() for p in folder.iterdir()}
    case.read_inputs(root, manifest)
    assert calls and before == {p: p.read_bytes() for p in folder.iterdir()}
    (folder / "METRICS.json").write_text('{"changed":true}\n')
    with pytest.raises(ValueError, match="hash mismatch"):
        case.read_inputs(root, manifest)
    manifest["evidence"]["commit"] = "wrong"
    with pytest.raises(ValueError, match="revision"):
        case.read_inputs(root, manifest)


def test_cli_rejects_evidence_destination_before_evaluation(tmp_path, monkeypatch):
    monkeypatch.setattr(sys, "argv", ["case", "--evidence-checkout", str(tmp_path),
                                     "--output", str(tmp_path / "result.json")])
    monkeypatch.setattr(case, "evaluate_checkout", lambda _: pytest.fail("evaluation must not start"))
    with pytest.raises(SystemExit):
        case.main()
    assert not (tmp_path / "result.json").exists()


def test_no_legacy_import_native_execution_or_network():
    source = Path(case.__file__).read_text()
    tree = ast.parse(source)
    imports = [node.module or "" for node in ast.walk(tree) if isinstance(node, ast.ImportFrom)]
    imports += [alias.name for node in ast.walk(tree) if isinstance(node, ast.Import) for alias in node.names]
    assert not any(n.startswith(("tools.", "socket", "requests", "urllib", "taichi")) for n in imports)
    process_calls = [node for node in ast.walk(tree) if isinstance(node, ast.Call)
                     and isinstance(node.func, ast.Attribute) and isinstance(node.func.value, ast.Name)
                     and node.func.value.id == "subprocess"]
    assert len(process_calls) == 1
    assert process_calls[0].func.attr == "check_output"
    assert not any(n.startswith("tools.sci_md_rheology") for n in sys.modules)
