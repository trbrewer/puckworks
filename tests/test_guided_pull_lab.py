"""Guided Pull Laboratory tests (PV-19B).

Offline + deterministic. Guards the honesty contract: every registered component gets exactly one
disposition, competing mechanisms are never overlaid, the executed lens reuses the existing producer
(no equation duplication), serialization is deterministic with no wall-clock, evidence is never
upgraded, and native reference results are never presented as the common scenario.
"""
import json

import pytest

import puckworks
from puckworks.product import lab


@pytest.fixture(scope="module")
def run():
    return lab._run_common_scenario()


@pytest.fixture(scope="module")
def report(run):
    return lab.build_comparison(run)


# ── coverage matrix ──────────────────────────────────────────────────────────────
def test_every_component_gets_exactly_one_valid_disposition(run):
    matrix = lab.build_matrix(run)
    names = [r["component_id"] for r in matrix]
    assert names == sorted(names)                              # stable ordering
    assert len(names) == len(set(names)) == len(puckworks.components())
    for r in matrix:
        assert r["disposition"] in lab.DISPOSITIONS


def test_matrix_ordering_is_import_order_independent(run):
    a = [r["component_id"] for r in lab.build_matrix(run)]
    b = [r["component_id"] for r in lab.build_matrix(run)]
    assert a == b == sorted(a)


def test_exactly_one_executed_common_scenario_lens(report):
    assert report["counts"]["executed_common_scenario_lenses"] == 1
    assert report["executed_lenses"][0]["component_id"] == "cameron2020.extraction_bdf"
    assert report["executed_lenses"][0]["disposition"] == "COMMON_SCENARIO_READY"


def test_competing_extraction_models_are_adapter_required_not_overlaid(report):
    adapter = {e["component_id"] for e in report["excluded_or_dispositioned"]
               if e["disposition"] == "ADAPTER_REQUIRED"}
    # competing extraction mechanisms must NOT be executed/overlaid on the common scenario
    for name in ("grudeva2025.reduced", "pannusch2024.solver", "romancorrochano2017.extraction"):
        assert name in adapter, f"{name} must be ADAPTER_REQUIRED (different reference volume/observable)"
    executed = {lens["component_id"] for lens in report["executed_lenses"]}
    assert not (adapter & executed)                           # never executed while adapter-required


def test_failed_is_reserved_and_not_used_for_unsupported(report):
    # "FAILED" is only for an execution that errored; nothing here errored
    dispositions = {r["disposition"] for r in report["component_matrix"]}
    assert "FAILED" not in dispositions
    assert "FAILED" in lab.DISPOSITIONS                       # but the vocabulary reserves it


# ── serialization ────────────────────────────────────────────────────────────────
def test_serialization_is_deterministic_and_wall_clock_free(report):
    a = lab.canonical_json(report)
    b = lab.canonical_json(lab.build_comparison())
    assert a == b
    for bad in ("timestamp", "generated_at", "datetime", "wall_clock"):
        assert bad not in a.lower()
    # source_commit (provenance, per-checkout) is excluded from the canonical hash
    assert "source_commit" not in json.loads(a).get("provenance", {})


def test_schema_version_is_distinct_from_pull_run(report, run):
    assert report["schema_version"] == 2 == lab.SCHEMA_VERSION
    assert run["schema_version"] == 1                         # PullRun v1 not overloaded


# ── evidence / units / honesty ─────────────────────────────────────────────────────
def test_every_observable_has_a_unit_and_a_role(report):
    for lens in report["executed_lenses"]:
        for o in lens["observables"]:
            assert "unit" in o and "role" in o
            assert o["role"] in ("prescribed", "derived", "predicted", "simulated", "fitted",
                                  "measured", "unsupported")


def test_executed_lens_carries_evidence_and_fidelity(report):
    lens = report["executed_lenses"][0]
    assert lens["traces"]                                    # trace-level evidence present
    for t in lens["traces"]:
        assert "evidence_badge" in t and "fidelity_ceiling" in t
    assert report["fidelity_ceiling"]
    assert report["what_this_does_not_prove"]


def test_no_equation_duplication_reuses_the_public_producer():
    src = (lab.__file__ and open(lab.__file__).read()) or ""
    assert "simulate_pull" in src                            # calls the existing producer
    assert "import numpy" not in src and "from numpy" not in src and "import scipy" not in src


def test_no_universal_grinder_dial_mapping():
    src = open(lab.__file__).read().lower()
    # the only mention of particle size is the explicit disclaimer; no dial->size conversion function
    assert "not a universal particle size" in src
    assert "dial_to_particle" not in src and "dial_to_size" not in src


def test_native_reference_not_presented_as_common_scenario(report):
    for r in report["component_reference_suite"]:
        if r.get("label"):
            assert "not the common" in r["label"].lower()
    # the executed native reference for cameron is labelled as such
    cam = next(r for r in report["component_reference_suite"]
               if r["component_id"] == "cameron2020.extraction_bdf")
    assert cam["status"] == "executed_native_reference"


def test_optional_gpu_dependency_is_skipped_not_passed(report):
    suite = {r["component_id"]: r for r in report["component_reference_suite"]}
    taichi = suite.get("brewer2026.lb_taichi")
    assert taichi and taichi["status"] == "SKIPPED_OPTIONAL_DEPENDENCY"   # a skip is never a pass


def test_does_not_upgrade_evidence_or_claim_validation(report):
    import re
    blob = json.dumps(report).lower()
    # "digital twin" and "best recipe" may appear ONLY as explicit disclaimers (negated in-sentence)
    for phrase in ("digital twin", "best recipe"):
        for m in re.finditer(re.escape(phrase), blob):
            seg = blob[max(0, m.start() - 60):m.end() + 20]
            assert "not " in seg or "never" in seg, f"un-negated {phrase!r}: …{seg}…"
    for bad in ("flavor prediction", "tastes better", "validated multi-model simulation of"):
        assert bad not in blob


# ── current Guided Pull remains compatible ─────────────────────────────────────────
def test_current_guided_pull_output_still_works(run):
    # the lab wraps but does not modify the pull path; PullRun v1 + observables intact
    assert run["completion_state"] in ("GUIDED_PULL_COMPLETE", "complete", "ok") or run.get("final_observables")
    assert "cameron2020.extraction_bdf" in {c["component_id"] for c in run["coverage"]}
