"""Rights preflight for the Guided Pull Laboratory public boundary (Phase 2, #73).

Public Laboratory execution and public output publication must be rights-gated BEFORE any model or
native-reference producer runs. This module resolves, for a request and an explicit execution context,
the code-execution and output-publication eligibility of every selected common lens and native reference,
and returns a deterministic preflight verdict. A blocked public request is represented explicitly and
carries NO scientific output — only the rights decision.

Execution context is explicit (never inferred from an environment variable's mere presence):

* ``LOCAL_PRIVATE`` / ``CI_VERIFICATION_NO_PUBLISH`` — inspection; a component runs unless its code is
  RIGHTS_BLOCKED (``rights.may_execute_locally``); nothing is published.
* ``PUBLIC_BATCH`` — public execution; requires AFFIRMATIVE code clearance
  (``rights.may_execute_in_public_batch``).
* ``PUBLIC_ARTIFACT`` — public execution AND public publication of scientific outputs; additionally
  requires AFFIRMATIVE output-redistribution clearance (``rights.may_publish_outputs``).
"""
from __future__ import annotations

EXECUTION_CONTEXTS = ("LOCAL_PRIVATE", "CI_VERIFICATION_NO_PUBLISH", "PUBLIC_BATCH", "PUBLIC_ARTIFACT")
_PUBLIC_EXECUTION = {"PUBLIC_BATCH", "PUBLIC_ARTIFACT"}
_PUBLISHES_OUTPUT = {"PUBLIC_ARTIFACT"}


def _requested_components(request) -> list:
    """(component_id, use_kind) for every selected common lens + resolved native reference. An unknown id
    is surfaced distinctly rather than silently dropped."""
    from puckworks.product import lab
    items: list = []
    try:
        for cid in lab.resolve_lens_selection(request):
            items.append((cid, "common_lens", None))
    except ValueError as exc:
        items.append((None, "common_lens", f"unknown lens id: {exc}"))
    try:
        for cid in lab._resolve_reference_component_ids(request):
            items.append((cid, "native_reference", None))
    except ValueError as exc:
        items.append((None, "native_reference", f"unknown reference id: {exc}"))
    return items


def preflight(request, context: str) -> dict:
    """Deterministic rights preflight. Returns a verdict dict with one row per requested component; a
    public request is blocked when any selected component's required clearance is not affirmative. No
    scientific output is produced or referenced here."""
    if context not in EXECUTION_CONTEXTS:
        raise ValueError(f"execution context must be one of {EXECUTION_CONTEXTS}, got {context!r}")
    from puckworks import rights
    public = context in _PUBLIC_EXECUTION
    publishes = context in _PUBLISHES_OUTPUT
    rows, blockers = [], []
    for cid, kind, err in _requested_components(request):
        if err is not None:                              # an unknown component id is a distinct block
            rows.append({"component_id": None, "use_kind": kind, "unknown": True, "blocked": True,
                         "blocker": err})
            blockers.append(err)
            continue
        rec = rights.rights_record(cid)
        code = (rights.may_execute_in_public_batch(cid) if public else rights.may_execute_locally(cid))
        out = rights.may_publish_outputs(cid)
        code_ok = code.allowed
        out_ok = out.allowed if publishes else True
        blocked = (not code_ok) or (publishes and not out_ok)
        blocker = ""
        if not code_ok:
            blocker = f"code execution not cleared for {context} ({code.governing_state})"
        elif publishes and not out_ok:
            blocker = f"output publication not cleared ({out.governing_state})"
        row = {
            "component_id": cid, "use_kind": kind, "context": context,
            "code_rights_state": rec.code_rights_state, "data_rights_state": rec.data_rights_state,
            "output_redistribution_state": rec.output_redistribution_state,
            "code_execution_allowed": code_ok,
            "output_publication_required": publishes, "output_publication_allowed": out_ok,
            "blocked": blocked, "blocker": blocker,
            "decision_source": "puckworks.rights use-specific policy",
            "review_issue": rec.decision_issue or "#73",
        }
        rows.append(row)
        if blocked:
            blockers.append(f"{cid}: {blocker}")
    return {"report": "puckworks-lab-rights-preflight", "context": context,
            "requested": rows, "blocked": bool(blockers), "blockers": blockers,
            "note": "a blocked public request produces NO scientific output; only this rights decision"}


def assert_public_cleared(request, context: str) -> dict:
    """Run the preflight and raise RightsGateBlocked if a public request is blocked. Returns the verdict
    when clear."""
    verdict = preflight(request, context)
    if verdict["blocked"]:
        raise RightsGateBlocked(verdict)
    return verdict


class RightsGateBlocked(Exception):
    """Raised when a public execution/publication request is blocked by the rights preflight. Carries the
    deterministic verdict (rights decision only, no scientific output)."""

    def __init__(self, verdict: dict):
        self.verdict = verdict
        super().__init__("; ".join(verdict["blockers"]) or "rights preflight blocked")
