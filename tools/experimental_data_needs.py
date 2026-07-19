"""Puckworks experimental-data campaign catalog: validate, list, show, and render (Phase 3, #46).

Reads ``docs/data_requests/experimental_campaigns.yml`` — the machine-readable catalog of the
measurements Puckworks needs — validates it against the live registry (components, gates), the quantity
ontology, and the structured measurement-agenda blockers, and renders a deterministic Markdown table into
a marker-bounded section of ``docs/EXPERIMENTAL_DATA_NEEDS.md``.

CLI::

    python tools/experimental_data_needs.py verify        # exit 1 on any problem
    python tools/experimental_data_needs.py list
    python tools/experimental_data_needs.py show EXP-001
    python tools/experimental_data_needs.py render         # rewrite the generated table section
    python tools/experimental_data_needs.py render --check  # fail if the table is stale
"""
from __future__ import annotations

import argparse
import re
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
CATALOG = _REPO / "docs" / "data_requests" / "experimental_campaigns.yml"
NEEDS_DOC = _REPO / "docs" / "EXPERIMENTAL_DATA_NEEDS.md"
_MARK_START = "<!-- BEGIN GENERATED CAMPAIGN TABLE -->"
_MARK_END = "<!-- END GENERATED CAMPAIGN TABLE -->"

_ID_RE = re.compile(r"^EXP-\d{3}$")
_ISSUE_RE = re.compile(r"^#\d+$")
_PLACEHOLDERS = ("DESIGN_CALCULATION_REQUIRED", "SENSOR_SELECTION_REQUIRED", "PILOT_REQUIRED",
                 "REQUIRED_FROM_CONTRIBUTOR")
_WALL_CLOCK = ("timestamp", "generated_at", "datetime", "wall_clock", "now(")
# finite unit vocabulary the catalog may use (extend deliberately, never silently)
_UNITS = {"s", "bar", "g", "g/s", "degC", "%", "-", "m", "m^2", "mm", "um", "mg", "kg/m^3",
          "bar; g/s", "not_applicable"}

_REQUIRED_FIELDS = (
    "campaign_id", "title", "status", "priority", "scientific_question", "decision_enabled",
    "target_components", "target_gates", "quantity_definitions", "required_observables",
    "required_metadata", "current_evidence", "evidence_gap", "evidence_ceiling",
    "measurement_agenda_blockers", "related_issues", "code_rights_expectation",
    "data_rights_expectation", "output_rights_expectation", "data_license_status",
    "submission_instructions",
)


def load_catalog(path: Path = CATALOG) -> dict:
    import yaml
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def _registry_ids():
    import puckworks
    from puckworks.product import quantity_semantics as qs
    from puckworks.validation import gates as G
    components = {c.name for c in puckworks.components()}
    gates = {n for n in dir(G) if n.startswith("gate_")}
    quantities = {qs.CAMERON_EY.quantity_id} | {q.quantity_id for q in qs._CANDIDATE_OUTPUT.values()}
    return components, gates, quantities


def _agenda_blocker_ids() -> set:
    from puckworks.product import quantity_semantics as qs
    return {a["blocker_id"] for a in qs.measurement_agenda()}


def validate(catalog: dict | None = None) -> list:
    cat = catalog or load_catalog()
    problems: list = []
    campaigns = cat.get("campaigns", [])
    components, gates, quantities = _registry_ids()
    evidence_levels = set(cat.get("evidence_levels", []))
    ids = [c.get("campaign_id") for c in campaigns]
    if ids != sorted(ids):
        problems.append("campaigns are not in stable sorted order")
    if len(ids) != len(set(ids)):
        problems.append("duplicate campaign_id")
    mapped_blockers: set = set()
    for c in campaigns:
        cid = c.get("campaign_id", "?")
        for f in _REQUIRED_FIELDS:
            if f not in c:
                problems.append(f"{cid}: missing required field {f!r}")
        if not _ID_RE.match(str(c.get("campaign_id", ""))):
            problems.append(f"{cid}: campaign_id must match EXP-NNN")
        # a campaign must name at least one model or gate decision
        if not c.get("target_components") and not c.get("target_gates"):
            problems.append(f"{cid}: names no target component or gate")
        for comp in c.get("target_components", []):
            if comp not in components:
                problems.append(f"{cid}: unknown target component {comp!r}")
        for g in c.get("target_gates", []):
            if g not in gates:
                problems.append(f"{cid}: unknown target gate {g!r}")
        for q in c.get("quantity_definitions", []):
            if q not in quantities:
                problems.append(f"{cid}: unknown quantity definition {q!r}")
        for obs in c.get("required_observables", []):
            u = obs.get("unit")
            if u not in _UNITS:
                problems.append(f"{cid}: observable {obs.get('name')!r} has unknown unit {u!r}")
        ev = c.get("current_evidence")
        if ev not in evidence_levels:
            problems.append(f"{cid}: current_evidence {ev!r} not in evidence_levels")
        for iss in c.get("related_issues", []):
            if not _ISSUE_RE.match(str(iss)):
                problems.append(f"{cid}: related issue {iss!r} is not #NNN")
        for b in c.get("measurement_agenda_blockers", []):
            mapped_blockers.add(b)
        # no wall-clock / no private absolute path anywhere in the record
        blob = str(c).lower()
        for w in _WALL_CLOCK:
            if w in blob:
                problems.append(f"{cid}: contains a wall-clock token {w!r}")
        if re.search(r"/users/|/home/|/private/", blob):
            problems.append(f"{cid}: contains a private absolute path")
    # every structured measurement-agenda blocker is mapped to a campaign (or explicitly deferred)
    agenda = _agenda_blocker_ids()
    deferred = set(cat.get("deferred_blockers", []))
    for b in sorted(agenda):
        if b not in mapped_blockers and b not in deferred:
            problems.append(f"measurement-agenda blocker {b!r} is not mapped to a campaign or deferred")
    for b in sorted(mapped_blockers):
        if b not in agenda:
            problems.append(f"campaign references a non-existent measurement-agenda blocker {b!r}")
    return problems


def render_table(catalog: dict | None = None) -> str:
    cat = catalog or load_catalog()
    lines = ["| Campaign | Priority | Decision enabled | Target components | Evidence | Blockers mapped |",
             "|---|---|---|---|---|---|"]
    for c in cat.get("campaigns", []):
        comps = ", ".join(f"`{x}`" for x in c.get("target_components", [])) or "—"
        blk = ", ".join(f"`{x}`" for x in c.get("measurement_agenda_blockers", [])) or "—"
        title = c.get("title", "").replace("|", "\\|")
        dec = c.get("decision_enabled", "").replace("|", "\\|")
        lines.append(f"| **{c['campaign_id']}** {title} | {c.get('priority')} | {dec} | {comps} | "
                     f"{c.get('current_evidence')} | {blk} |")
    return "\n".join(lines) + "\n"


def _write_generated_table(check: bool = False) -> int:
    text = NEEDS_DOC.read_text(encoding="utf-8")
    if _MARK_START not in text or _MARK_END not in text:
        print("EXPERIMENTAL_DATA_NEEDS.md is missing the generated-table markers")
        return 1
    table = render_table()
    new = re.sub(re.escape(_MARK_START) + r".*?" + re.escape(_MARK_END),
                 _MARK_START + "\n" + table + _MARK_END, text, flags=re.S)
    if check:
        if new != text:
            print("generated campaign table is stale (run: python tools/experimental_data_needs.py render)")
            return 1
        print("generated campaign table is current")
        return 0
    NEEDS_DOC.write_text(new, encoding="utf-8")
    print(f"wrote generated campaign table ({len(load_catalog()['campaigns'])} campaigns)")
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="experimental_data_needs", description=__doc__)
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("verify")
    sub.add_parser("list")
    s = sub.add_parser("show")
    s.add_argument("campaign_id")
    r = sub.add_parser("render")
    r.add_argument("--check", action="store_true")
    args = ap.parse_args(argv)
    if args.cmd == "verify":
        problems = validate()
        if problems:
            print("CAMPAIGN CATALOG INVALID:")
            for p in problems:
                print("  -", p)
            return 1
        print(f"campaign catalog OK: {len(load_catalog()['campaigns'])} campaigns valid")
        return 0
    if args.cmd == "list":
        for c in load_catalog().get("campaigns", []):
            print(f"{c['campaign_id']}  P{c.get('priority')}  {c.get('current_evidence'):22}  {c['title']}")
        return 0
    if args.cmd == "show":
        import json
        c = next((x for x in load_catalog()["campaigns"] if x["campaign_id"] == args.campaign_id), None)
        if c is None:
            print(f"no campaign {args.campaign_id!r}")
            return 1
        print(json.dumps(c, indent=2, sort_keys=True, ensure_ascii=False))
        return 0
    return _write_generated_table(check=args.check)


if __name__ == "__main__":
    raise SystemExit(main())
