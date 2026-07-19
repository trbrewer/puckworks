"""One rights-safe Laboratory execution service (accessibility mission Phase 1, #43 / #70).

Every interactive and batch surface — the Actions batch, the Colab notebook, and the Streamlit apps —
runs a Laboratory request through THIS service, so the ordering and the rights boundary live in exactly
one place:

  validate context  ->  rights preflight (BEFORE any producer)  ->  execute scenario/lenses  ->
  execute selected native references  ->  build comparison.

Guarantees:

* the caller must pass an explicit execution context from the finite vocabulary (never inferred);
* the rights preflight runs BEFORE any common-scenario or native-reference producer — one blocked
  selection blocks the whole request before every producer;
* ``LOCAL_PRIVATE`` keeps ``NOT_REVIEWED`` inspectable and refuses only ``RIGHTS_BLOCKED``;
  ``PUBLIC_BATCH`` requires affirmative code clearance; ``PUBLIC_ARTIFACT`` additionally requires
  affirmative output-publication clearance (all delegated to ``lab_rights_gate.preflight``);
* a blocked request returns a typed blocked result carrying ONLY the rights decision — no scientific
  report, trace, observable, native-reference result, or scientific hash.

Serialization/rendering stays with each surface; this service never writes a file or renders a figure.
"""
from __future__ import annotations

import dataclasses


@dataclasses.dataclass(frozen=True)
class LabRequestResult:
    """The outcome of one Laboratory request under an explicit execution context. When ``blocked`` is
    true the result carries the rights decision ONLY (``report is None``); a scientific report is present
    only for an allowed request."""
    execution_context: str
    blocked: bool
    rights_preflight: dict            # deterministic preflight verdict (always present)
    selected_component_ids: tuple     # every selected common lens + native reference id (deterministic)
    blockers: tuple = ()
    report: dict | None = None        # the ComparisonRun — ONLY when not blocked

    def __post_init__(self):
        if self.blocked and self.report is not None:
            raise ValueError("a blocked LabRequestResult must carry no scientific report")
        if not self.blocked and self.report is None:
            raise ValueError("an allowed LabRequestResult must carry a scientific report")

    @property
    def has_science(self) -> bool:
        return self.report is not None

    def blocked_record(self) -> dict:
        """The serializable blocked record — rights decision + context + selection ONLY, never science.
        Safe to publish for a denied request."""
        return {"report": "puckworks-lab-request-blocked", "execution_context": self.execution_context,
                "blocked": True, "selected_component_ids": list(self.selected_component_ids),
                "blockers": list(self.blockers), "rights_preflight": self.rights_preflight}


class LabRequestBlocked(Exception):
    """Raised by ``execute_lab_request(..., raise_on_block=True)`` when the preflight blocks. Carries the
    typed blocked result (rights decision only, no scientific output)."""

    def __init__(self, result: LabRequestResult):
        self.result = result
        super().__init__("; ".join(result.blockers) or "rights preflight blocked")


def _selected_component_ids(verdict: dict) -> tuple:
    return tuple(sorted({r["component_id"] for r in verdict["requested"] if r.get("component_id")}))


def execute_lab_request(request, *, execution_context: str, provenance=None,
                        raise_on_block: bool = False) -> LabRequestResult:
    """Run one Laboratory request under an explicit execution context, rights preflight FIRST.

    Returns a :class:`LabRequestResult`. A blocked request returns ``blocked=True`` with ``report=None``
    (no producer ran); with ``raise_on_block=True`` it raises :class:`LabRequestBlocked` carrying the same
    typed result. An allowed request returns the full ``ComparisonRun`` in ``report``.
    """
    from puckworks.product import lab, lab_rights_gate as gate
    if execution_context not in gate.EXECUTION_CONTEXTS:
        raise ValueError(f"execution_context must be one of {gate.EXECUTION_CONTEXTS}, "
                         f"got {execution_context!r}")
    # RIGHTS PREFLIGHT — resolves every selected common lens + native reference and decides, BEFORE any
    # producer runs. A blocked (or unknown-id) selection blocks the whole request here.
    verdict = gate.preflight(request, execution_context)
    selected = _selected_component_ids(verdict)
    if verdict["blocked"]:
        result = LabRequestResult(execution_context=execution_context, blocked=True,
                                  rights_preflight=verdict, selected_component_ids=selected,
                                  blockers=tuple(verdict["blockers"]), report=None)
        if raise_on_block:
            raise LabRequestBlocked(result)
        return result
    # cleared: producers may now run (lenses, then native references, then comparison assembly)
    execution = lab.execute_scenario(request)
    report = lab.build_comparison(execution, provenance=provenance)
    return LabRequestResult(execution_context=execution_context, blocked=False,
                            rights_preflight=verdict, selected_component_ids=selected,
                            blockers=(), report=report)
