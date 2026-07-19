"""Producer-free public Explorer catalog (accessibility mission Phase 2, #43 / #70).

A plain-language view of the FULL component registry that runs NO scientific producer. It reuses only the
authoritative committed catalog (``puckworks.product.lab_catalog``, itself producer-free) and the
centralized rights registry (``puckworks.rights``). It constructs no ``ScenarioExecution``, runs no
Cameron lens, runs no native-reference / validation producer, and emits NO scientific-payload hash — the
response is catalog metadata only, safe to render on a public page with no scientific execution.

The public web Explorer and the notebook "catalog only" mode both consume this.
"""
from __future__ import annotations

# plain-language phrasing for the espresso stage (no invented model name; the component id is authoritative)
_STAGE_PLAIN = {
    "extraction": "how coffee dissolves out of the grounds",
    "flow": "how water moves through the puck",
    "packing": "how the ground coffee is packed",
    "bed_dynamics": "how the puck changes during the shot",
    "machine": "the espresso machine's behaviour",
}
_ROLE_PLAIN = {
    "runtime": "runs a shot-scale simulation",
    "calibration": "a calibration / verification model",
    "reference": "a reference-only model",
}


def _validity_summary(validity_range) -> str:
    if validity_range is None:
        return ""
    return str(validity_range)


def _unavailable_reason(entry) -> str:
    """A concise, plain reason a component is not publicly live (rights first, then executability)."""
    from puckworks import rights
    if rights.is_code_rights_blocked(entry.component_id):
        return "rights-blocked: this model may not run publicly"
    if not entry.public_execution_eligible:
        return "public execution not yet rights-reviewed (a visible gap, not a clearance)"
    if not entry.output_publication_eligible:
        return "output publication not yet rights-cleared"
    return ""


def explorer_row(entry) -> dict:
    """One producer-free Explorer row for a catalog entry. Rights code/data/output states are kept
    SEPARATE; public-live availability is the conjunction of affirmative public-execution AND
    output-publication clearance (never code-clearance alone, never NOT_REVIEWED)."""
    public_live = bool(entry.public_execution_eligible and entry.output_publication_eligible)
    return {
        "component_id": entry.component_id,
        "plain_stage": _STAGE_PLAIN.get(entry.stage, entry.stage),
        "plain_role": _ROLE_PLAIN.get(entry.execution_role, entry.execution_role),
        "reference": entry.doi or entry.module,          # human-readable source (no invented plain name)
        "stage": entry.stage,
        "model_role": entry.execution_role,
        "evidence_strength": entry.evidence_strength,
        "validity_range": _validity_summary(entry.validity_range),
        "common_scenario_ready": entry.disposition == "COMMON_SCENARIO_READY",
        "native_reference_ready": entry.native_runner_id is not None,
        "native_runner_id": entry.native_runner_id,
        "adapter_required": entry.adapter_capability == "ADAPTER_REQUIRED",
        # rights are use-specific and kept separate — never collapse code/data/output into one flag
        "code_rights_state": entry.code_rights_state,
        "data_rights_state": entry.data_rights_state,
        "output_redistribution_state": entry.output_redistribution_state,
        "public_live_available": public_live,
        "unavailable_reason": "" if public_live else _unavailable_reason(entry),
        "disposition": entry.disposition,
    }


def explorer_catalog() -> dict:
    """The full producer-free Explorer catalog: one row per registered component, deterministic order.
    Runs NO producer and carries NO scientific-payload hash. ``public_live_component_ids`` is the set that
    a public surface may offer as live-runnable (affirmative rights only)."""
    from puckworks.product import lab_catalog
    entries = sorted(lab_catalog.build_catalog(), key=lambda e: e.component_id)   # producer-free
    rows = [explorer_row(e) for e in entries]
    live = sorted(r["component_id"] for r in rows if r["public_live_available"])
    return {
        "report": "puckworks-lab-explorer",
        "producer_free": True,                           # no scientific producer ran to build this
        "n_components": len(rows),
        "components": rows,
        "public_live_component_ids": live,
        "note": ("catalog metadata only — no scientific producer ran, and there is no scientific-payload "
                 "hash; public-live availability is per-component and affirmative-rights-only"),
    }


def public_live_component_ids() -> list:
    """The components a PUBLIC surface may offer as live-runnable today (affirmative public-execution AND
    output-publication clearance). Derived from use-specific rights, never hard-coded."""
    return explorer_catalog()["public_live_component_ids"]
