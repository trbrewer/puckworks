"""Centralized component rights registry (issue #73).

One authoritative rights record per registered component, keeping **code**, **data**, and **output**
redistribution rights distinct — an article's licence is not a licence for a solver's *code*. This is
the single source of rights truth: product/lab code consumes it rather than carrying its own dictionary.

An absent review is ``NOT_REVIEWED`` — never silently ``CLEAR``. Only ``RIGHTS_BLOCKED`` blocks new Lab
execution / native runners / adapters / release artifacts; ``NOT_REVIEWED`` is surfaced (a visible gap),
not a positive clearance.

This module runs no git subprocess and imports the registry lazily to avoid an import cycle.
"""
from __future__ import annotations

import dataclasses

# finite project rights vocabulary
RIGHTS_STATES = (
    "CLEAR",                       # reviewed and unrestricted for the stated use
    "PERMISSION_DOCUMENTED",       # restricted, but written permission is on record (metadata summary)
    "INDEPENDENT_REIMPLEMENTATION",  # independently derived from permitted equations/data
    "RIGHTS_REVIEW_REQUIRED",      # a determination is needed before the stated use
    "RIGHTS_BLOCKED",              # must NOT be used for the stated use
    "NOT_REVIEWED",                # no rights review has been performed (default; a gap, not a clearance)
    "NOT_APPLICABLE",
)

# states that must block new Lab execution / runners / adapters / release inclusion
_BLOCKING = {"RIGHTS_BLOCKED"}


@dataclasses.dataclass(frozen=True)
class RightsRecord:
    component_id: str
    code_rights_state: str
    data_rights_state: str
    output_redistribution_state: str
    rights_note: str = ""
    source: str = ""                # evidence for the determination (non-private)
    decision_issue: str = ""
    review_date: str = ""           # ISO date the determination was made (empty if never reviewed)

    def __post_init__(self):
        for field in ("code_rights_state", "data_rights_state", "output_redistribution_state"):
            v = getattr(self, field)
            if v not in RIGHTS_STATES:
                raise ValueError(f"{self.component_id}: {field}={v!r} not in RIGHTS_STATES")

    @property
    def is_code_blocked(self) -> bool:
        return self.code_rights_state in _BLOCKING

    @property
    def any_blocked(self) -> bool:
        return any(s in _BLOCKING for s in (self.code_rights_state, self.data_rights_state,
                                            self.output_redistribution_state))

    def to_dict(self) -> dict:
        return dataclasses.asdict(self)


# ── authoritative per-component records (only reviewed components are listed) ──────────
# grudeva2025.reduced: the module self-documents a direct "FAITHFUL PORT" of the upstream solver
# github.com/YoanaGrudeva/espresso-model, which declares NO licence (all-rights-reserved). The EJAM
# article (CC-BY, DOI 10.1017/S095679252500018X) rights are SEPARATE and do NOT license the solver code
# or the code derived from it. Decision pending in #73; no numerics changed by this record.
_RECORDS: dict[str, RightsRecord] = {
    "grudeva2025.reduced": RightsRecord(
        component_id="grudeva2025.reduced",
        code_rights_state="RIGHTS_BLOCKED",
        data_rights_state="RIGHTS_REVIEW_REQUIRED",
        output_redistribution_state="RIGHTS_BLOCKED",
        rights_note=(
            "Legacy: a self-documented direct port of the unlicensed upstream solver "
            "(YoanaGrudeva/espresso-model, licence: null); no documented permission. The EJAM article "
            "(CC-BY) licenses the equations/text, NOT the solver code — the two are tracked separately. "
            "Retained in history and the current package pending the #73 decision; not for new Lab "
            "execution, native runners, adapters, or a newly approved release artifact."),
        source=("module header self-description ('FAITHFUL PORT ... rather than re-deriving'); upstream "
                "GitHub licence=null (re-verified); MANIFEST 'reference repo (no explicit license)'; "
                "issue #73"),
        decision_issue="#73",
        review_date="2026-07-18"),
}


def rights_record(component_id: str) -> RightsRecord:
    """The authoritative rights record for a component; unreviewed components return a NOT_REVIEWED
    record (never a silent CLEAR)."""
    rec = _RECORDS.get(component_id)
    if rec is not None:
        return rec
    return RightsRecord(component_id=component_id, code_rights_state="NOT_REVIEWED",
                        data_rights_state="NOT_REVIEWED", output_redistribution_state="NOT_REVIEWED",
                        rights_note="no rights review on record", source="", decision_issue="",
                        review_date="")


def all_rights() -> list[RightsRecord]:
    """One rights record for every registered component (deterministic order)."""
    import puckworks
    return [rights_record(c.name) for c in sorted(puckworks.components(), key=lambda c: c.name)]


def is_code_rights_blocked(component_id: str) -> bool:
    return rights_record(component_id).is_code_blocked


def blocked_components() -> list[str]:
    """Registered components whose code rights are blocked (must not enter new execution/release)."""
    return sorted(r.component_id for r in all_rights() if r.is_code_blocked)
