"""Executable-capability availability matrix (Paper 3 MC7) and implementation status (MC8).

MC7's point: the title calls the registry "executable", but the repository holds at least eight
different notions of availability, and they are not equivalent. A component can be registered but
rights-blocked, importable but missing its data, runnable locally but not publicly hostable. Saying
"all 27 components are executable" flattens all of that into one word.

This module answers the question per component, per dimension, and — critically — marks how each
answer was obtained:

``derived``   computed from the registry, the rights records or the filesystem
``declared``  a stated judgement recorded here, because nothing in the repo derives it

The distinction is the honest part. A matrix that silently mixed the two would look more rigorous
than it is, which is the failure mode this whole paper is about.

MC8's point is different: it asks about CAPABILITIES rather than components — "is first-class
adapter support implemented, or architectural intent?" That is not derivable from a component
registry at all, so `IMPLEMENTATION_STATUS` is explicitly a declared table, with each row carrying
the evidence that supports its claim.

CLI::

    python -m puckworks.paper3.availability             # human-readable
    python -m puckworks.paper3.availability --json      # machine-readable (MC7 asks for this)
    python -m puckworks.paper3.availability --verify    # fail if the generated tables are stale
"""
from __future__ import annotations

import importlib
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
GENERATED = REPO_ROOT / "docs" / "paper3_resource" / "generated"
MATRIX_JSON = GENERATED / "availability_matrix.json"
MATRIX_MD = GENERATED / "availability_matrix.md"
STATUS_JSON = GENERATED / "implementation_status.json"
STATUS_MD = GENERATED / "implementation_status.md"

#: The eight dimensions MC7 enumerates, in its order.
DIMENSIONS = (
    "registered",
    "importable",
    "runnable_local",
    "required_data_available",
    "scientifically_eligible",
    "redistribution_license_status",
    "public_hosting_status",
    "included_in_release",
)

#: Components whose gates need data that is NOT in the repository (retrieval-only or rights-blocked
#: deposits). Recorded here with the reason, because "the gate did not run" and "the data is not
#: present" are different facts and only the second belongs in this column.
DATA_NOT_PRESENT: dict[str, str] = {
    "grudeva2025.reduced": "source code and data are rights-blocked; nothing is vendored",
}


#: MC8 — implemented capability vs architectural intent, per CAPABILITY rather than per component.
#: This table is DECLARED, not derived, and says so: no registry field answers "is first-class
#: adapter support implemented or intended?". Each row therefore carries the evidence that supports
#: its claim, so a reader can check the judgement instead of trusting it.
#:
#: Columns follow MC8's list: specified / implemented / gated / used in a demonstration /
#: in the stable release / dev-main only / publicly hosted.
_S = ("specified", "implemented", "gated", "demonstrated", "in_release", "dev_main_only", "public")
IMPLEMENTATION_STATUS: tuple[dict, ...] = (
    dict(capability="Typed stage contracts with unit assertions at boundaries",
         specified=True, implemented=True, gated=True, demonstrated=True,
         in_release=True, dev_main_only=False, public=True,
         evidence="puckworks/contracts.py + SCHEMA_VERSION; boundary assertions exercised by the "
                  "quick gates"),
    dict(capability="First-class adapters between components",
         specified=True, implemented=True, gated=True, demonstrated=True,
         in_release=True, dev_main_only=False, public=True,
         evidence="puckworks/product/linked_pull adapters; the relay's audited run records 7 "
                  "adapter hand-offs. NOT automatic: each adapter is written and reviewed."),
    dict(capability="Arbitrary multi-stage configuration (any component set composes)",
         specified=True, implemented=False, gated=False, demonstrated=False,
         in_release=False, dev_main_only=False, public=False,
         evidence="ARCHITECTURAL INTENT. The registry makes incompatibilities VISIBLE and supports "
                  "SELECTED explicit configurations; it does not prove compatibility or synthesize "
                  "an arbitrary chosen set. The failed swelling composition (§5) is the worked "
                  "example of why."),
    dict(capability="Observables stage",
         specified=True, implemented=False, gated=False, demonstrated=False,
         in_release=False, dev_main_only=False, public=False,
         evidence="ARCHITECTURAL INTENT. The stage exists in the taxonomy and holds zero registered "
                  "components; Table 1 is generated, so the emptiness is visible rather than "
                  "asserted."),
    dict(capability="Named-shot scorecard generated from producers",
         specified=True, implemented=True, gated=True, demonstrated=True,
         in_release=False, dev_main_only=True, public=False,
         evidence="puckworks/paper3/named_shot_scorecard.py with --verify and a CI guard; landed "
                  "after v0.3.0, so it is dev-main only."),
    dict(capability="Deterministic redistributable archive with per-member manifest",
         specified=True, implemented=True, gated=True, demonstrated=True,
         in_release=False, dev_main_only=True, public=False,
         evidence="puckworks/paper3/archive.py; byte-identical across builds, verifies without the "
                  "source checkout; post-v0.3.0."),
    dict(capability="Community-corpus ingestion workflow",
         specified=True, implemented=True, gated=False, demonstrated=True,
         in_release=False, dev_main_only=True, public=False,
         evidence="Harvest path exists and the §7.4 demo runs, but the canonical historical corpus "
                  "is NOT obtainable through the public API, so no gate depends on it."),
    dict(capability="Rights preflight before any producer call",
         specified=True, implemented=True, gated=True, demonstrated=True,
         in_release=True, dev_main_only=False, public=True,
         evidence="puckworks/rights.py + product/lab_rights_gate.py; fail-closed for public paths."),
)


def implementation_status() -> dict:
    counts = {c: sum(1 for r in IMPLEMENTATION_STATUS if r[c]) for c in _S}
    intent_only = [r["capability"] for r in IMPLEMENTATION_STATUS if not r["implemented"]]
    return dict(columns=list(_S), n_capabilities=len(IMPLEMENTATION_STATUS), counts=counts,
                architectural_intent_only=intent_only, how="declared with per-row evidence",
                rows=[dict(r) for r in IMPLEMENTATION_STATUS])


def render_implementation_status(s: dict) -> str:
    out = [
        "<!-- generated by puckworks.paper3.availability — do not edit by hand -->",
        "",
        f"**Implementation status — {s['n_capabilities']} capabilities.** This table is "
        "**declared**, not derived: no registry field distinguishes an implemented capability from "
        "an architectural one. Each row carries the evidence for its claim. "
        f"**{len(s['architectural_intent_only'])} of {s['n_capabilities']} capabilities are "
        "architectural intent rather than current functionality.**",
        "",
        "| capability | spec | impl | gated | demo | release | dev-main | public | evidence |",
        "|---|:--:|:--:|:--:|:--:|:--:|:--:|:--:|---|",
    ]
    tick = {True: "✓", False: "—"}
    for r in s["rows"]:
        out.append("| {c} | {a} | {b} | {g} | {d} | {rel} | {dm} | {p} | {e} |".format(
            c=r["capability"], a=tick[r["specified"]], b=tick[r["implemented"]],
            g=tick[r["gated"]], d=tick[r["demonstrated"]], rel=tick[r["in_release"]],
            dm=tick[r["dev_main_only"]], p=tick[r["public"]], e=r["evidence"]))
    return "\n".join(out) + "\n"


def _gate_backed(component) -> bool:
    return bool(getattr(component, "gates", ()) or ())


def _importable(component) -> tuple[bool, str]:
    """Resolve a component's implementation.

    Two conventions exist and conflating them produces a false negative. Model components name a
    MODULE (`puckworks.models.cameron2020.extraction_bdf`); calibration components sourced straight
    from a dataset name a `module:attribute` pointer (`puckworks.data:pump_characteristic_ulka`).
    Importing the latter as a module raises ModuleNotFoundError — which is a fact about the check,
    not about the component. A first pass here reported three perfectly good calibration entries as
    unimportable for exactly that reason.
    """
    target = component.module
    attr = ""
    if ":" in target:
        target, _, attr = target.partition(":")
    try:
        mod = importlib.import_module(target)
    except Exception as exc:                       # pragma: no cover - failure path
        return False, f"{type(exc).__name__}: {exc}"
    if attr and not hasattr(mod, attr):
        return False, f"{target} imported but has no attribute {attr!r}"
    return True, f"importlib resolved {component.module}"


def component_row(component) -> dict:
    """One component's availability across all eight dimensions, each tagged derived/declared."""
    import puckworks.rights as rights

    cid = component.name
    ok_import, import_err = _importable(component)
    local = rights.may_execute_locally(cid)
    public = rights.may_execute_in_public_batch(cid)
    code_rel = rights.may_include_code_in_release(cid)
    data_rel = rights.may_include_data_in_release(cid)
    record = rights.rights_record(cid)

    data_present = cid not in DATA_NOT_PRESENT

    row = {
        "component": cid,
        "stage": component.stage,
        "registered": {"value": True, "how": "derived", "why": "present in registry.components()"},
        "importable": {"value": ok_import, "how": "derived",
                       "why": import_err or f"importlib imported {component.module}"},
        "runnable_local": {"value": bool(local.allowed), "how": "derived",
                           "why": f"rights[{local.governing_field}]={local.governing_state}: {local.reason}"},
        "required_data_available": {
            "value": data_present, "how": "derived" if data_present else "declared",
            "why": DATA_NOT_PRESENT.get(cid, "no recorded data blocker; gates resolve their inputs")},
        # Scientific admissibility is the registry's own evidence axis. It is NOT a boolean: a
        # component with `qualitative` evidence is admissible for illustration and not for a
        # quantitative claim, which is exactly the distinction this paper argues for.
        "scientifically_eligible": {
            "value": component.evidence_strength, "how": "derived",
            "why": f"registry evidence_strength; gate-backed={_gate_backed(component)}"},
        "redistribution_license_status": {
            "value": f"code:{code_rel.governing_state}/data:{data_rel.governing_state}",
            "how": "derived",
            "why": f"code {'allowed' if code_rel.allowed else 'refused'}; "
                   f"data {'allowed' if data_rel.allowed else 'refused'}"},
        "public_hosting_status": {"value": bool(public.allowed), "how": "derived",
                                  "why": f"rights[{public.governing_field}]={public.governing_state}: {public.reason}"},
        # Every registered component ships in the wheel; what differs is whether its rights permit
        # the CODE to be redistributed, which is the previous column. Kept separate because MC7
        # lists them separately and conflating them is the error it warns about.
        "included_in_release": {"value": bool(code_rel.allowed), "how": "derived",
                                "why": "packaged in the wheel; gated on code redistribution rights"},
        "blocking_reason": (record.rights_note if not local.allowed
                            else DATA_NOT_PRESENT.get(cid, "")),
    }
    return row


def matrix() -> dict:
    import puckworks.models  # noqa: F401  (registers components)
    from puckworks import registry as R

    rows = [component_row(c) for c in sorted(R.components(), key=lambda c: c.name)]

    counts: dict[str, dict] = {}
    for dim in DIMENSIONS:
        vals: dict[str, int] = {}
        for r in rows:
            v = r[dim]["value"]
            key = str(v)
            vals[key] = vals.get(key, 0) + 1
        counts[dim] = dict(sorted(vals.items(), key=lambda kv: (-kv[1], kv[0])))

    derived = sum(1 for r in rows for d in DIMENSIONS if r[d]["how"] == "derived")
    declared = sum(1 for r in rows for d in DIMENSIONS if r[d]["how"] == "declared")
    return dict(n_components=len(rows), dimensions=list(DIMENSIONS), counts=counts,
                n_cells_derived=derived, n_cells_declared=declared, rows=rows)


def render_matrix(m: dict) -> str:
    """Markdown. Reports COUNTS PER DIMENSION, which is MC7's specific ask — the manuscript must
    stop saying "all N components are executable" and start saying how many are what."""
    out = [
        "<!-- generated by puckworks.paper3.availability — do not edit by hand -->",
        "",
        f"**Availability matrix — {m['n_components']} registered components, "
        f"{len(m['dimensions'])} dimensions.** "
        f"{m['n_cells_derived']} of {m['n_cells_derived'] + m['n_cells_declared']} cells are "
        "*derived* from the registry, the rights records or the filesystem; the remainder are "
        "*declared* and carry their reason.",
        "",
        "| dimension | counts |",
        "|---|---|",
    ]
    for dim in m["dimensions"]:
        pairs = ", ".join(f"`{k}`: {v}" for k, v in m["counts"][dim].items())
        out.append(f"| {dim} | {pairs} |")
    out += ["", "**Per component.**", "",
            "| component | stage | importable | local | data | evidence | public | release | blocker |",
            "|---|---|---|---|---|---|---|---|---|"]
    for r in m["rows"]:
        out.append("| `{c}` | {s} | {i} | {l} | {d} | {e} | {p} | {rel} | {b} |".format(
            c=r["component"], s=r["stage"],
            i="yes" if r["importable"]["value"] else "**no**",
            l="yes" if r["runnable_local"]["value"] else "**no**",
            d="yes" if r["required_data_available"]["value"] else "**no**",
            e=r["scientifically_eligible"]["value"],
            p="yes" if r["public_hosting_status"]["value"] else "no",
            rel="yes" if r["included_in_release"]["value"] else "no",
            b=(r["blocking_reason"] or "—")[:60]))
    return "\n".join(out) + "\n"


def write() -> dict:
    m, s = matrix(), implementation_status()
    GENERATED.mkdir(parents=True, exist_ok=True)
    MATRIX_JSON.write_text(json.dumps(m, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    MATRIX_MD.write_text(render_matrix(m), encoding="utf-8")
    STATUS_JSON.write_text(json.dumps(s, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    STATUS_MD.write_text(render_implementation_status(s), encoding="utf-8")
    return dict(matrix=m, implementation_status=s)


def verify() -> list[str]:
    """Fail if the committed artifacts differ from a fresh computation."""
    problems = []
    m, s = matrix(), implementation_status()
    for path, fresh in ((MATRIX_JSON, json.dumps(m, indent=2, sort_keys=True) + "\n"),
                        (MATRIX_MD, render_matrix(m)),
                        (STATUS_JSON, json.dumps(s, indent=2, sort_keys=True) + "\n"),
                        (STATUS_MD, render_implementation_status(s))):
        if not path.exists():
            problems.append(f"missing generated artifact: {path.relative_to(REPO_ROOT)}")
        elif path.read_text(encoding="utf-8") != fresh:
            problems.append(f"STALE: {path.relative_to(REPO_ROOT)} differs from a fresh computation")
    return problems


MANUSCRIPT = REPO_ROOT / "docs" / "PAPER_3_PUCKWORKS_DRAFT.md"
_BLOCKS = (("<!-- availability:begin -->", "<!-- availability:end -->",
            lambda: render_matrix(matrix())),
           ("<!-- implstatus:begin -->", "<!-- implstatus:end -->",
            lambda: render_implementation_status(implementation_status())))


def splice(write_it: bool = True) -> str:
    """Write both tables into the manuscript between markers, or report staleness.

    Same convention as the named-shot scorecard: the manuscript owns the prose, the producer owns
    the table, and a CI guard fails if they drift.
    """
    text = MANUSCRIPT.read_text(encoding="utf-8")
    problems = []
    for begin, end, build in _BLOCKS:
        if begin not in text or end not in text:
            problems.append(f"markers {begin} missing from the manuscript")
            continue
        block = begin + "\n" + build() + end
        current = begin + text.split(begin, 1)[1].split(end, 1)[0] + end
        if current.strip() != block.strip():
            if write_it:
                text = text.split(begin)[0] + block + text.split(end, 1)[1]
            else:
                problems.append(f"{begin[:-4]} table is STALE -- run --splice")
    if write_it and not problems:
        MANUSCRIPT.write_text(text, encoding="utf-8")
    return "; ".join(problems)


def main(argv=None) -> int:
    argv = sys.argv[1:] if argv is None else list(argv)
    if "--splice" in argv:
        problem = splice(write_it=True)
        print(problem or "manuscript tables spliced")
        return 1 if problem else 0
    if "--verify" in argv:
        problems = verify()
        stale = splice(write_it=False)
        if stale:
            problems.append(stale)
        for p in problems:
            print("  -", p, file=sys.stderr)
        print("availability artifacts up to date." if not problems else "availability STALE")
        return 1 if problems else 0
    if "--write" in argv:
        write()
    if "--json" in argv:
        print(json.dumps(dict(matrix=matrix(), implementation_status=implementation_status()),
                         indent=2, sort_keys=True))
    else:
        print(render_matrix(matrix()))
        print()
        print(render_implementation_status(implementation_status()))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
