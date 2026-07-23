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

import copy
import dataclasses
import datetime
import re
from types import MappingProxyType


def _freeze(obj):
    """Recursively convert dicts→read-only proxies and lists→tuples (deep immutability)."""
    if isinstance(obj, dict):
        return MappingProxyType({k: _freeze(v) for k, v in obj.items()})
    if isinstance(obj, (list, tuple)):
        return tuple(_freeze(v) for v in obj)
    return obj


def _thaw(obj):
    """Inverse of _freeze: proxies→plain dicts, tuples→lists, for JSON-safe serialization."""
    if isinstance(obj, MappingProxyType):
        return {k: _thaw(v) for k, v in obj.items()}
    if isinstance(obj, tuple):
        return [_thaw(v) for v in obj]
    return obj

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
# affirmative clearances — the ONLY states that positively permit a public/outward or release use
_AFFIRMATIVE = {"CLEAR", "PERMISSION_DOCUMENTED", "INDEPENDENT_REIMPLEMENTATION"}
# a determination is on record but is not a positive clearance (a visible gap, never "clear")
_GAP = {"NOT_REVIEWED", "RIGHTS_REVIEW_REQUIRED"}

_ISO_DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")

# finite use vocabulary for the use-specific policy layer
RIGHTS_USES = (
    "local_execution", "public_batch_execution", "output_publication",
    "code_in_release", "data_in_release",
)


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
    permission: dict = dataclasses.field(default_factory=dict)  # non-private permission metadata summary
    tombstone: bool = False         # a record for a removed component (registry existence not required)

    _STATE_FIELDS = ("code_rights_state", "data_rights_state", "output_redistribution_state")

    def __post_init__(self):
        states = [getattr(self, f) for f in self._STATE_FIELDS]
        for field, v in zip(self._STATE_FIELDS, states):
            if v not in RIGHTS_STATES:                   # rejects any lowercase/local vocabulary too
                raise ValueError(f"{self.component_id}: {field}={v!r} not in RIGHTS_STATES")
        if self.review_date:
            # regex fixes the exact YYYY-MM-DD shape (fromisoformat alone is lenient about
            # separators on 3.11+); fromisoformat then rejects impossible calendar dates
            # (e.g. 2026-99-99) that a shape-only check would accept.
            if not _ISO_DATE.match(self.review_date):
                raise ValueError(f"{self.component_id}: review_date {self.review_date!r} is not ISO YYYY-MM-DD")
            try:
                datetime.date.fromisoformat(self.review_date)
            except ValueError:
                raise ValueError(f"{self.component_id}: review_date {self.review_date!r} is not a valid calendar date")
        # deep-freeze the permission metadata: deepcopy defends against a caller mutating the
        # dict they passed in; _freeze makes the record's own copy read-only at every level.
        object.__setattr__(self, "permission", _freeze(copy.deepcopy(dict(self.permission))))
        # a reviewed determination (anything past NOT_REVIEWED) must cite evidence + a review date
        reviewed = any(s != "NOT_REVIEWED" for s in states)
        if reviewed and not (self.source and self.review_date):
            raise ValueError(f"{self.component_id}: a reviewed rights determination requires a nonempty "
                             f"source and review_date")
        if any(s in _BLOCKING for s in states) and not (self.decision_issue and self.rights_note):
            raise ValueError(f"{self.component_id}: RIGHTS_BLOCKED requires a decision_issue and a reason "
                             f"(rights_note)")
        if any(s == "PERMISSION_DOCUMENTED" for s in states) and not self.permission:
            raise ValueError(f"{self.component_id}: PERMISSION_DOCUMENTED requires permission metadata")
        if any(s == "NOT_APPLICABLE" for s in states) and not self.rights_note:
            raise ValueError(f"{self.component_id}: NOT_APPLICABLE requires a documented reason "
                             f"(rights_note)")

    @property
    def is_code_blocked(self) -> bool:
        return self.code_rights_state in _BLOCKING

    @property
    def any_blocked(self) -> bool:
        return any(s in _BLOCKING for s in (self.code_rights_state, self.data_rights_state,
                                            self.output_redistribution_state))

    def to_dict(self) -> dict:
        # asdict cannot pickle the frozen mapping proxy; build the dict directly and thaw
        # permission back to plain JSON-safe containers.
        d = {f.name: getattr(self, f.name) for f in dataclasses.fields(self)}
        d["permission"] = _thaw(self.permission)
        return d


# ── authoritative per-component records (only reviewed components are listed) ──────────
# grudeva2025.reduced: the module self-documents a direct "FAITHFUL PORT" of the upstream solver
# github.com/YoanaGrudeva/espresso-model, which declares NO licence (all-rights-reserved). The EJAM
# article (CC-BY, DOI 10.1017/S095679252500018X) rights are SEPARATE and do NOT license the solver code
# or the code derived from it. Decision pending in #73; no numerics changed by this record.
# brewer2026.lb_reference: a FIRST-PARTY, in-repo numerical code-verification component. The module
# (puckworks/models/brewer2026/lb_reference.py) is authored entirely in this repository (git blame:
# 138/138 lines Tim Brewer; introduced c54a2a6 "puckworks v0.1.0"); it carries no port/copy/upstream
# licence marker (contrast grudeva2025's self-documented "faithful port"). Its verification INPUT is
# generated synthetically in code — the authoritative gate gate_lb_channel constructs a plane-channel
# `solid` boolean array in memory and compares the solved lattice permeability to the ANALYTIC
# plane-Poiseuille reference k = h^2/12; NO third-party experimental dataset is read, bundled, or
# redistributed. The generated OUTPUT (simulated lattice permeability, analytic reference, relative
# error) is therefore first-party numerical content. This is code-verification only — NOT coffee/espresso
# validation. Decision issue #70. This record is bounded to the LB channel code-verification path and
# clears NOTHING else (see rights_review_notes.md).
_RECORDS: dict[str, RightsRecord] = {
    "brewer2026.lb_reference": RightsRecord(
        component_id="brewer2026.lb_reference",
        code_rights_state="CLEAR",
        data_rights_state="NOT_APPLICABLE",
        output_redistribution_state="CLEAR",
        rights_note=(
            "First-party Puckworks LB plane-channel code-verification path only. Code: in-repo D3Q19 TRT "
            "kernel authored by the maintainer (no port/copy). Data: NOT_APPLICABLE — the verification "
            "input (channel `solid` array) is generated synthetically in code; no third-party dataset is "
            "bundled or redistributed. Output: first-party numerical results (simulated permeability, "
            "analytic k=h^2/12 reference, relative error). Scope is exactly this LB channel verification "
            "runner and its outputs — this is NOT coffee-bed/espresso validation, and it clears NO other "
            "component, author, model class, or namespace."),
        source=("first-party module puckworks/models/brewer2026/lb_reference.py (git blame: 138/138 lines "
                "Tim Brewer; introduced c54a2a6 'puckworks v0.1.0'; no port/copy/licence marker); the "
                "authoritative gate puckworks.validation.gates.gate_lb_channel builds a synthetic plane "
                "channel in code and compares to the analytic plane-Poiseuille k=h^2/12 (no bundled "
                "dataset); issue #70"),
        decision_issue="#70",
        review_date="2026-07-19"),
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


# ── use-specific rights policy ───────────────────────────────────────────────────────
# One rights state is NOT universally sufficient: a component may be inspectable locally yet not cleared
# for public execution, output redistribution, or release inclusion. Each use consults the relevant
# code/data/output field with the strictness that use demands.
@dataclasses.dataclass(frozen=True)
class RightsUseDecision:
    component_id: str
    use: str                 # one of RIGHTS_USES
    governing_field: str     # which rights field governed this use
    governing_state: str
    allowed: bool            # may this use proceed?
    severity: str            # "clear" | "gap" | "blocked" | "not_applicable"
    reason: str

    def to_dict(self) -> dict:
        return dataclasses.asdict(self)


def _severity(state: str) -> str:
    if state in _BLOCKING:
        return "blocked"
    if state in _AFFIRMATIVE:
        return "clear"
    if state == "NOT_APPLICABLE":
        return "not_applicable"
    return "gap"


def _decide(component_id: str, use: str, field: str, state: str, *, mode: str) -> RightsUseDecision:
    """mode: 'dev' (inspectable unless blocked), 'outward' (affirmative clearance required), 'release'
    (hard-block only on RIGHTS_BLOCKED; gaps ship but are reported)."""
    sev = _severity(state)
    if mode == "outward":
        allowed = state in _AFFIRMATIVE
        reason = ("affirmatively cleared" if allowed else
                  "blocked" if sev == "blocked" else
                  "no output/use to publish" if sev == "not_applicable" else
                  "not cleared for public/outward use — review required (NOT_REVIEWED is not clear)")
    else:  # 'dev' and 'release' both hard-block only on RIGHTS_BLOCKED
        allowed = state not in _BLOCKING
        reason = ("blocked" if sev == "blocked" else
                  "affirmatively cleared" if sev == "clear" else
                  "not applicable" if sev == "not_applicable" else
                  ("inspectable in development; not a clearance" if mode == "dev"
                   else "ships as a reported gap; not a clearance"))
    return RightsUseDecision(component_id, use, field, state, allowed, sev, reason)


def may_execute_locally(component_id: str) -> RightsUseDecision:
    r = rights_record(component_id)
    return _decide(component_id, "local_execution", "code_rights_state", r.code_rights_state, mode="dev")


def may_execute_in_public_batch(component_id: str) -> RightsUseDecision:
    r = rights_record(component_id)
    return _decide(component_id, "public_batch_execution", "code_rights_state", r.code_rights_state,
                   mode="outward")


def may_publish_outputs(component_id: str) -> RightsUseDecision:
    r = rights_record(component_id)
    return _decide(component_id, "output_publication", "output_redistribution_state",
                   r.output_redistribution_state, mode="outward")


def may_include_code_in_release(component_id: str) -> RightsUseDecision:
    r = rights_record(component_id)
    return _decide(component_id, "code_in_release", "code_rights_state", r.code_rights_state,
                   mode="release")


def may_include_data_in_release(component_id: str) -> RightsUseDecision:
    r = rights_record(component_id)
    return _decide(component_id, "data_in_release", "data_rights_state", r.data_rights_state,
                   mode="release")


# ── record-set validation (registry existence, duplicates, tombstones) ───────────────
def validate_records(records: dict | None = None, registered: set | None = None) -> list[str]:
    """Validate the authoritative record set: each key matches its record's component_id, non-tombstone
    records name a registered component, and there are no duplicate component_ids. Returns problems
    (empty == clean)."""
    recs = _RECORDS if records is None else records
    if registered is None:
        import puckworks
        registered = {c.name for c in puckworks.components()}
    problems: list[str] = []
    seen: set[str] = set()
    for key, rec in recs.items():
        if key != rec.component_id:
            problems.append(f"record key {key!r} != component_id {rec.component_id!r}")
        if rec.component_id in seen:
            problems.append(f"duplicate rights record for {rec.component_id!r}")
        seen.add(rec.component_id)
        if not rec.tombstone and rec.component_id not in registered:
            problems.append(f"rights record {rec.component_id!r} names no registered component "
                            f"(mark tombstone=True if the component was removed)")
    return problems


# ── rights-review backlog (a visible gap list; affirmative records only from real evidence) ──
def review_backlog(*, runner_ids=(), adapter_ids=(), release_component_ids=None,
                   data_fixtures=()) -> list[dict]:
    """A structured backlog of the rights reviews still owed, derived from the registry + the centralized
    records. Every unreviewed/blocked-for-the-use item is surfaced; nothing is asserted CLEAR here."""
    import puckworks
    comps = {c.name for c in puckworks.components()}
    rel = comps if release_component_ids is None else set(release_component_ids)
    items: list[dict] = []

    def add(component_id, use, decision):
        items.append({"component_id": component_id, "use": use,
                      "governing_state": decision.governing_state, "severity": decision.severity,
                      "needs_review": decision.severity in ("gap",) or not decision.allowed,
                      "reason": decision.reason})

    # every registered component: local + public execution + output publication
    for cid in sorted(comps):
        add(cid, "local_execution", may_execute_locally(cid))
        add(cid, "public_batch_execution", may_execute_in_public_batch(cid))
        add(cid, "output_publication", may_publish_outputs(cid))
    # native runners (their outputs may enter a public Actions artifact)
    for cid in sorted(set(runner_ids)):
        add(cid, "public_batch_execution", may_execute_in_public_batch(cid))
        add(cid, "output_publication", may_publish_outputs(cid))
    # proposed common-scenario adapters
    for cid in sorted(set(adapter_ids)):
        add(cid, "public_batch_execution", may_execute_in_public_batch(cid))
    # everything that would enter the wheel
    for cid in sorted(rel):
        add(cid, "code_in_release", may_include_code_in_release(cid))
        add(cid, "data_in_release", may_include_data_in_release(cid))
    # data fixtures included in the wheel
    for fx in sorted(set(data_fixtures)):
        items.append({"component_id": fx, "use": "data_in_release", "governing_state": "NOT_REVIEWED",
                      "severity": "gap", "needs_review": True,
                      "reason": "packaged data fixture — redistribution rights not yet reviewed"})
    return items
