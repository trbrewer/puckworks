"""Deterministic research registry-impact review (issue #46, channel B).

Reads the metadata-only intake records under ``docs/research/intake/``, the model cards under
``docs/cards/``, and the LIVE component registry, and reports the model/registry-impact deltas a human
must triage. It is **read-only and offline**: it never modifies a card, registry entry, model, claim,
or evidence label, never downloads anything, and never authorizes implementation (a disposition is not
an authorization).

Identity is DOI -> arXiv id -> normalized title (first available); duplicates are reported, never
silently dropped. Output is deterministic canonical JSON and a human-readable Markdown report.

CLI::

    python tools/research_impact.py report --format md
    python tools/research_impact.py report --format json
    python tools/research_impact.py validate      # just validate the intake records

The report does NOT store full text or private locators; those are rejected by intake validation.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
INTAKE_DIR = _REPO / "docs" / "research" / "intake"
CARDS_DIR = _REPO / "docs" / "cards"
SCHEMA_PATH = INTAKE_DIR / "schema.json"

# substrings that must never appear in an intake record value (private-locator / full-text guard)
_FORBIDDEN_SUBSTRINGS = ("?token=", "&token=", "access_token", "sharept", "sharing?", "/private/",
                         "-----begin", "authorization:", "bearer ", "ghp_", "gho_")

_ACCESS_STATES = {"metadata_only", "open_access", "project_private_review", "rights_pending",
                  "redistribution_prohibited", "redistribution_permitted"}
_REDIST_STATES = {"rights_pending", "redistribution_prohibited", "redistribution_permitted",
                  "not_applicable"}
_DISPOSITIONS = {"metadata_only", "data-access-and-license-review", "full-text-review", "rights-review",
                 "already-carded", "duplicate", "superseded", "implement-candidate", "no-action"}


# ── identity ──────────────────────────────────────────────────────────────────────
def normalize_title(title: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", (title or "").lower()).strip()


def record_identity(rec: dict) -> str:
    doi = (rec.get("doi") or "").strip().lower()
    if doi:
        return "doi:" + doi.replace("https://doi.org/", "").lstrip("/")
    ax = (rec.get("arxiv_id") or "").strip().lower()
    if ax:
        return "arxiv:" + ax.replace("arxiv:", "")
    return "title:" + normalize_title(rec.get("title", ""))


# ── intake loading + validation (schema-lite; no jsonschema dependency required) ────
def _load_yaml(path: Path) -> dict:
    import yaml
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def load_schema() -> dict:
    return json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))


def validate_record(rec: dict, schema: dict, *, source: str = "") -> list:
    """Return a list of validation problems for one intake record (empty == clean)."""
    problems = []
    props = schema.get("properties", {})
    allowed = set(props)
    for req in schema.get("required", []):
        if req not in rec or rec[req] in (None, ""):
            problems.append(f"{source}: missing required field '{req}'")
    for k in rec:
        if k.startswith("_"):
            continue                      # internal loader annotations (not part of the record)
        if k not in allowed:
            problems.append(f"{source}: unknown field '{k}' (schema forbids extra fields)")
    sid = rec.get("stable_id", "")
    if sid and not re.fullmatch(r"[a-z0-9][a-z0-9_]{2,63}", str(sid)):
        problems.append(f"{source}: stable_id '{sid}' is not a valid slug")
    if rec.get("access_state") not in _ACCESS_STATES:
        problems.append(f"{source}: invalid access_state {rec.get('access_state')!r}")
    if rec.get("redistribution_state") not in _REDIST_STATES:
        problems.append(f"{source}: invalid redistribution_state {rec.get('redistribution_state')!r}")
    if rec.get("disposition") not in _DISPOSITIONS:
        problems.append(f"{source}: invalid disposition {rec.get('disposition')!r}")
    pd = rec.get("published_date")
    if pd not in (None, "") and not re.fullmatch(r"\d{4}-\d{2}-\d{2}", str(pd)):
        problems.append(f"{source}: published_date '{pd}' is not YYYY-MM-DD")
    # length caps + private-locator / full-text guard
    for k, v in rec.items():
        text = " ".join(v) if isinstance(v, list) else ("" if v is None else str(v))
        low = text.lower()
        for bad in _FORBIDDEN_SUBSTRINGS:
            if bad in low:
                problems.append(f"{source}: field '{k}' contains a forbidden private/full-text token")
        maxlen = props.get(k, {}).get("maxLength")
        if maxlen and isinstance(v, str) and len(v) > maxlen:
            problems.append(f"{source}: field '{k}' exceeds maxLength {maxlen}")
    return problems


# ── source scope: committed (tracked-only, canonical/CI) vs working_tree (local authoring) ──
SOURCE_SCOPES = ("committed", "working_tree")


def _tracked_repo_files(root: Path = _REPO) -> set | None:
    """Repo-relative POSIX paths that git currently tracks, or None when this is not a git checkout
    (e.g. an installed sdist). Deterministic for a given commit/index — the basis of committed scope."""
    try:
        out = subprocess.run(["git", "-C", str(root), "ls-files", "-z"],
                             capture_output=True, text=True, check=True)
    except (OSError, subprocess.CalledProcessError):
        return None
    return {p for p in out.stdout.split("\0") if p}


def _rel(path: Path, root: Path) -> str | None:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return None


def _in_scope(path: Path, tracked: set | None, root: Path = _REPO) -> bool:
    """Whether a file on disk is in scope. committed scope (tracked is a set) admits only tracked files;
    working_tree scope (tracked is None) admits everything on disk."""
    if tracked is None:
        return True
    rel = _rel(path, root)
    return rel is None or rel in tracked                 # outside the repo -> always in scope


def scoped_glob(directory: Path, pattern: str, tracked: set | None, root: Path = _REPO) -> tuple:
    """Return (in_scope_paths, excluded_repo_paths) for a glob under committed/working_tree scope."""
    in_scope, excluded = [], []
    for p in sorted(directory.glob(pattern)):
        if _in_scope(p, tracked, root):
            in_scope.append(p)
        else:
            excluded.append(_rel(p, root) or str(p))
    return in_scope, excluded


def load_intake(intake_dir: Path = INTAKE_DIR, *, tracked: set | None = None,
                root: Path = _REPO) -> list:
    """Load and sort every intake record (by stable_id) for deterministic output. In committed scope
    (`tracked` is a set) untracked .yml files are excluded, not silently included."""
    schema = load_schema()
    records = []
    paths, _excluded = scoped_glob(intake_dir, "*.yml", tracked, root)
    for p in paths:
        rec = _load_yaml(p)
        rec["_source_file"] = p.name
        rec["_problems"] = validate_record(rec, schema, source=p.name)
        records.append(rec)
    records.sort(key=lambda r: r.get("stable_id", r["_source_file"]))
    return records


def dedupe(records: list) -> tuple:
    """Return (unique_by_identity, duplicate_groups) preserving all provenance."""
    by_id: dict[str, list] = {}
    for r in records:
        by_id.setdefault(record_identity(r), []).append(r)
    duplicates = {k: v for k, v in by_id.items() if len(v) > 1}
    unique = [v[0] for v in by_id.values()]
    unique.sort(key=lambda r: r.get("stable_id", ""))
    return unique, duplicates


# ── cards + registry ────────────────────────────────────────────────────────────
_STATUS_RE = re.compile(r"^\*\*Status:\*\*\s*(.+)$", re.M)
_DOI_RE = re.compile(r"10\.\d{4,9}/[^\s\)\]\"'<>]+")


def card_status(text: str) -> str:
    m = _STATUS_RE.search(text)
    return (m.group(1).strip() if m else "").lower()


# implemented-ish and proposed-ish leading status TOKENS (parsed from the first phrase only, so prose
# words like "nothing to implement" or "already registered and gated" never trigger a false match)
_IMPL_TOKENS = ("implemented", "gated", "intaken")
_PROPOSED_TOKENS = ("proposed", "card-only")


def status_token(status: str) -> str:
    """The leading status token: text before the first of ( — - , | : (en/em dash or ascii)."""
    lead = re.split(r"[(—–|:]|\s-\s|\s->\s|\s→\s", status, maxsplit=1)[0].strip()
    return lead


def load_cards(cards_dir: Path = CARDS_DIR, *, tracked: set | None = None,
               root: Path = _REPO) -> dict:
    cards = {}
    paths, _excluded = scoped_glob(cards_dir, "*.md", tracked, root)
    for p in paths:
        if p.stem.upper() == "TEMPLATE":       # the card template is not a real card
            continue
        text = p.read_text(encoding="utf-8", errors="replace")
        st = card_status(text)
        cards[p.stem] = {
            "key": p.stem, "path": f"docs/cards/{p.name}",
            "status": st, "status_token": status_token(st),
            "dois": sorted(set(_DOI_RE.findall(text))),
        }
    return cards


def cards_for_component(name: str, card_keys: set) -> set:
    """Associate a component id with its card(s): match on the name prefix, the suffix, or the
    dotted/underscored full name (covers e.g. sourcing2026.g1_glassbead_analog -> g1_glassbead_analog)."""
    prefix = name.split(".")[0].lower()
    suffix = name.split(".", 1)[1].lower() if "." in name else ""
    full_us = name.lower().replace(".", "_")
    out = set()
    for k in card_keys:
        kl = k.lower()
        if kl == prefix or (suffix and kl == suffix) or kl == full_us:
            out.add(k)
    return out


def _components() -> list:
    import puckworks
    return list(puckworks.components())


_STALE_CARD_STATUSES = ("card-only", "proposed")


def resolve_scope(source_scope: str, repo_root: Path = _REPO) -> tuple:
    """Return (resolved_scope, tracked_set). committed scope needs a git checkout; when git is absent it
    degrades to 'working_tree_fallback' (recorded, not silently canonicalized)."""
    if source_scope not in SOURCE_SCOPES:
        raise ValueError(f"source_scope must be one of {SOURCE_SCOPES}, got {source_scope!r}")
    if source_scope == "working_tree":
        return "working_tree", None
    tracked = _tracked_repo_files(repo_root)
    if tracked is None:
        return "working_tree_fallback", None            # not a git checkout: cannot scope to committed
    return "committed", tracked


def build_report(*, intake_dir: Path = INTAKE_DIR, cards_dir: Path = CARDS_DIR,
                 components=None, source_scope: str = "committed", repo_root: Path = _REPO) -> dict:
    """Compute the deterministic registry-impact report (no side effects, no network).

    Default 'committed' scope examines only git-tracked cards/intake, so the canonical artifact is
    reproducible from a commit and never silently incorporates a maintainer's untracked local files.
    'working_tree' scope includes untracked files for local authoring. Excluded untracked paths and the
    tracked/untracked split are recorded in the report."""
    if components is None:
        components = _components()
    resolved_scope, tracked = resolve_scope(source_scope, repo_root)
    cards = load_cards(cards_dir, tracked=tracked, root=repo_root)
    card_keys = set(cards)
    records = load_intake(intake_dir, tracked=tracked, root=repo_root)
    unique, dup_groups = dedupe(records)
    # what committed scope excluded (empty in working_tree scope and in a clean CI checkout)
    _, excluded_cards = scoped_glob(cards_dir, "*.md", tracked, repo_root)
    _, excluded_intake = scoped_glob(intake_dir, "*.yml", tracked, repo_root)
    excluded_untracked = sorted(excluded_cards + excluded_intake)

    # card DOIs (for stale-DOI + already-carded matching)
    card_dois = {d for c in cards.values() for d in c["dois"]}
    card_ids_by_doi = {}
    for c in cards.values():
        for d in c["dois"]:
            card_ids_by_doi.setdefault(d, []).append(c["key"])

    findings = []

    def add(category, severity, subject, detail):
        findings.append({"category": category, "severity": severity, "subject": subject,
                         "detail": detail})

    # ---- component-side checks (from the live registry) ----
    comp_cards = {}
    for comp in components:
        name = comp.name
        matched = cards_for_component(name, card_keys)
        comp_cards[name] = sorted(matched)
        paper = getattr(comp, "paper", "") or ""
        if not matched and not paper.strip():
            add("component_no_card_or_source", "high", name,
                "registered component has no matching card and no paper/source string")
        elif not matched:
            add("component_no_card", "medium", name,
                f"registered component has no matching card (paper: {paper[:80]})")
        if not getattr(comp, "gates", ()):  # empty gates tuple
            add("component_no_gate", "high", name, "registered component has no gate wired")
        # implemented/executable component whose card's LEADING status token still says card-only/proposed
        for k in matched:
            tok = cards[k]["status_token"]
            role = getattr(comp, "execution_role", "")
            if role in ("runtime", "calibration") and tok in _PROPOSED_TOKENS:
                add("component_card_status_stale", "high", name,
                    f"component is registered/executable ({role}) but card '{k}' status is "
                    f"'{cards[k]['status']}' (stale — should read implemented/gated)")

    carded_component_keys = {k for v in comp_cards.values() for k in v}

    # ---- card-side checks (use the LEADING status token, not prose) ----
    for key, c in cards.items():
        tok = c["status_token"]
        has_impl = key in carded_component_keys
        if not has_impl:
            if tok in _IMPL_TOKENS:
                # a card claiming implemented/gated with no mapped component: often a legitimate
                # data-only companion (a loader/closure, not a registry component) — flag for a human
                # to confirm it is data-only vs a genuinely missing registration.
                add("card_impl_status_no_component_review", "medium", key,
                    f"card status token '{tok}' but no registered component maps — confirm this is a "
                    "data-only companion, not a missing registration")
            elif tok in _PROPOSED_TOKENS:
                add("card_no_implementation", "info", key,
                    f"card status '{c['status']}' — proposed/card-only, no registered component (awaiting)")

    # ---- intake-side checks ----
    for r in unique:
        src = r.get("_source_file", r.get("stable_id"))
        if r.get("_problems"):
            add("intake_record_invalid", "high", src, "; ".join(r["_problems"]))
        ident = record_identity(r)
        doi = (r.get("doi") or "").lower()
        coupled = [k for k in (r.get("coupled_cards") or []) if k in card_keys]
        coupled_missing = [k for k in (r.get("coupled_cards") or []) if k not in card_keys]
        # source with no card at all (neither DOI match nor an existing coupled card)
        doi_carded = doi in card_dois
        if not coupled and not doi_carded:
            add("new_source_no_card", "medium", r.get("stable_id"),
                f"intake source '{r.get('title','')[:70]}' has no matching card yet")
        for k in coupled_missing:
            add("intake_coupled_card_missing", "medium", r.get("stable_id"),
                f"coupled_cards references '{k}' which is not a card file")
        # unresolved redistribution rights
        if r.get("redistribution_state") in ("rights_pending", "redistribution_prohibited"):
            add("rights_unresolved", "medium", r.get("stable_id"),
                f"redistribution_state={r.get('redistribution_state')} — review before any ingestion")
        # superseded records
        if r.get("disposition") == "superseded" or r.get("supersedes"):
            add("superseded_record", "info", r.get("stable_id"),
                f"supersedes={r.get('supersedes')}, disposition={r.get('disposition')}")
        # implement-candidate that is card-no-implementation
        if r.get("disposition") == "implement-candidate":
            impl_present = any(k in carded_component_keys for k in coupled)
            if coupled and not impl_present:
                add("card_no_implementation_intake", "medium", r.get("stable_id"),
                    f"implement-candidate coupled to card(s) {coupled} with no registered component "
                    f"(authorization is separate; see coupled_issue {r.get('coupled_issue')})")
        # human-review heuristics: validity narrowing / claim contradiction (keyword-flagged only)
        blob = " ".join(str(r.get(k, "")) for k in ("relevance", "notes")).lower()
        if re.search(r"\bnarrow(s|ing)?\b.*(valid|range|limit)", blob):
            add("possible_validity_narrowing", "info", r.get("stable_id"),
                "record language suggests it may narrow a validity range — human review")
        if re.search(r"\bcontradict|conflicts? with|inconsistent with\b", blob):
            add("possible_claim_contradiction", "info", r.get("stable_id"),
                "record language suggests a possible claim contradiction — human review")

    # ---- duplicates ----
    for ident, group in sorted(dup_groups.items()):
        add("duplicate_intake_records", "medium", ident,
            "shared identity across: " + ", ".join(r.get("stable_id", "?") for r in group))

    # ---- stale/superseded DOI cross-check (intake DOI not in any card while marked already-carded) ----
    for r in unique:
        if r.get("disposition") == "already-carded":
            doi = (r.get("doi") or "").lower()
            coupled = [k for k in (r.get("coupled_cards") or []) if k in card_keys]
            if doi and not any(doi in cards[k]["dois"] for k in coupled) and doi not in card_dois:
                add("stale_or_superseded_doi", "medium", r.get("stable_id"),
                    f"already-carded record DOI {doi} is not present in any matched card — "
                    "possible stale/superseded publication metadata")

    findings.sort(key=lambda f: (f["category"], f["subject"]))
    summary = {}
    for f in findings:
        summary[f["category"]] = summary.get(f["category"], 0) + 1

    return {
        "schema_version": 2,
        "report": "puckworks-research-impact",
        "authorizes_implementation": False,
        "source_scope": {
            "scope": resolved_scope,
            "requested_scope": source_scope,
            "tracked_card_count": len(cards),
            "tracked_intake_count": len(records),
            "untracked_card_count": len(excluded_cards),
            "untracked_intake_count": len(excluded_intake),
            "excluded_untracked_paths": excluded_untracked,
        },
        "counts": {
            "components": len(components),
            "cards": len(cards),
            "intake_records": len(records),
            "unique_sources": len(unique),
            "duplicate_groups": len(dup_groups),
            "findings": len(findings),
        },
        "findings_by_category": dict(sorted(summary.items())),
        "findings": findings,
    }


def canonical_json(report: dict) -> str:
    return json.dumps(report, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def render_markdown(report: dict) -> str:
    c = report["counts"]
    lines = [
        "# Puckworks research registry-impact report",
        "",
        "_Deterministic, offline, read-only. A disposition is **not** an implementation authorization; "
        "this report changes no card, registry entry, model, claim, or evidence label._",
        "",
        f"- components: **{c['components']}** · cards: **{c['cards']}** · intake records: "
        f"**{c['intake_records']}** (unique sources **{c['unique_sources']}**, duplicate groups "
        f"**{c['duplicate_groups']}**)",
        f"- findings: **{c['findings']}**",
    ]
    ss = report.get("source_scope")
    if ss:
        lines.append(
            f"- source scope: **{ss['scope']}** (requested `{ss['requested_scope']}`); "
            f"tracked cards **{ss['tracked_card_count']}**, untracked excluded "
            f"**{ss['untracked_card_count']} card(s) / {ss['untracked_intake_count']} intake**")
        if ss["excluded_untracked_paths"]:
            lines.append(f"  - excluded untracked: {', '.join('`'+p+'`' for p in ss['excluded_untracked_paths'])}")
    lines += [
        "",
        "## Findings by category",
        "",
    ]
    for cat, n in report["findings_by_category"].items():
        lines.append(f"- `{cat}`: {n}")
    lines += ["", "## Findings", ""]
    if not report["findings"]:
        lines.append("_No deltas detected._")
    for f in report["findings"]:
        lines.append(f"- **[{f['severity']}] {f['category']}** — `{f['subject']}`: {f['detail']}")
    lines.append("")
    return "\n".join(lines)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="research_impact", description=__doc__)
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("report", help="compute the registry-impact report")
    r.add_argument("--format", choices=["md", "json"], default="md")
    r.add_argument("--out", default=None, help="write to a file instead of stdout")
    r.add_argument("--source-scope", choices=list(SOURCE_SCOPES), default="committed",
                   help="committed (default; canonical/CI: tracked files only) or working_tree "
                        "(local authoring: include untracked files)")
    v = sub.add_parser("validate", help="validate intake records only")
    v.add_argument("--source-scope", choices=list(SOURCE_SCOPES), default="committed")
    args = ap.parse_args(argv)

    if args.cmd == "validate":
        _, tracked = resolve_scope(args.source_scope)
        records = load_intake(tracked=tracked)
        problems = [p for rec in records for p in rec.get("_problems", [])]
        if problems:
            print("INTAKE VALIDATION FAILED:")
            for p in problems:
                print("  -", p)
            return 1
        print(f"intake OK: {len(records)} record(s) valid")
        return 0

    report = build_report(source_scope=args.source_scope)
    text = canonical_json(report) if args.format == "json" else render_markdown(report)
    if args.out:
        Path(args.out).write_text(text, encoding="utf-8")
        print(f"wrote {args.out} ({len(report['findings'])} findings)")
    else:
        sys.stdout.write(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
