"""Regression: the Full Laboratory Tour's CLEAN-process result is stable and import-order invariant.

**Why this asserts a STRUCTURAL fingerprint, not the full scientific hash.**
The tour's ``tour_scientific_hash`` folds in each component's per-component ``scientific_hash``, which
for SCIENTIFIC_CHECK components covers floating-point ``gate_metric`` outputs. Those float values differ
across platform / numpy / scipy builds, so the full tour hash is **environment-dependent** and cannot be
a portable frozen literal: the same commit produced ``1b5e4505…`` on one machine and ``61e9010b…`` in CI.
An earlier attempt to freeze the full hash (``1c1434ef…`` → ``1b5e4505…``) was therefore inherently
fragile — it only ever matched the environment that last wrote it.

What IS portable, and what this test freezes, is the tour's STRUCTURE: for every component, its
``(component_id, stage, execution_kind, execution_status, #outputs, output_roles)``. That fingerprint is
float-free, so it is byte-identical across environments, and it still catches the changes that matter —
a component added/removed, a route change, a check flipping to FAILED/ERROR, and gate additions/removals
(which change a SCIENTIFIC_CHECK component's output count). Numeric-level determinism is guarded
separately and portably: within-environment by ``test_full_tour_hash_is_import_order_invariant`` (the
three import orders must agree) and per model by targeted tests (e.g. Cameron EY = 14.106). This test
also asserts the full float hash is a well-formed, within-run-deterministic value — it just does not pin
it to a cross-environment literal.

Historical note: the streamtube→Cameron ``C_S0`` import-time mutation (which made Cameron import-order
dependent and inflated its EY to ~17.06 % vs the intended 14.11 %) was fixed in the stabilization pass;
the import-order tests guard that it stays fixed.
"""
import hashlib
import json

import pytest

# PORTABLE, environment-independent structural fingerprint (pv19_named, LOCAL_PRIVATE): the sorted
# per-component (id, stage, kind, status, #outputs, output_roles). Update it ONLY for an intended
# structural change (component added/removed, route/status change, gate added/removed).
_BASELINE_TOUR_STRUCTURE = "1f9a54a7c7067ef50a0c8f1e6c4830e6a180b71dbc0947b03784e47234c7fbd4"


def _tour_structure_hash(tour) -> str:
    """A float-free fingerprint of the tour's routing/structure — portable across environments."""
    rows = sorted((r.component_id, r.stage, str(r.execution_kind), str(r.execution_status),
                   len(r.outputs or []), tuple(sorted(r.output_roles or [])))
                  for r in tour.components)
    return hashlib.sha256(json.dumps(rows, sort_keys=True, ensure_ascii=False).encode()).hexdigest()


def test_tour_manifest_unchanged():
    from puckworks.product import lab_tour
    assert lab_tour.FULL_LABORATORY_TOUR_V1 == "full_laboratory_tour_v1"
    assert lab_tour.verify_tour_manifest() == []


@pytest.mark.slow
@pytest.mark.scientific_baseline
def test_frozen_reference_request_reproduces_the_baseline_structure():
    from puckworks.product import lab, lab_tour
    tour = lab_tour.execute_laboratory_tour(lab.ScenarioRequest("pv19_named"),
                                            execution_context="LOCAL_PRIVATE")
    # (1) the portable structural fingerprint is frozen (catches membership/route/status/gate changes)
    assert _tour_structure_hash(tour) == _BASELINE_TOUR_STRUCTURE
    # (2) the full float hash is a well-formed sha256, but is NOT pinned to a cross-environment literal
    #     (it is platform/numpy dependent). Its within-environment determinism is guarded portably by
    #     test_full_tour_hash_is_import_order_invariant (three import orders must agree).
    h = tour.to_dict()["tour_scientific_hash"]
    assert isinstance(h, str) and len(h) == 64 and int(h, 16) >= 0       # well-formed sha256 hex


def test_full_tour_does_not_import_or_run_the_relay():
    import inspect

    from puckworks.product import lab_tour, lab_tour_insights
    for mod in (lab_tour, lab_tour_insights):
        src = inspect.getsource(mod)
        assert "linked_pull" not in src, f"{mod.__name__} must not reference the relay"
