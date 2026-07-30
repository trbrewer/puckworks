#!/usr/bin/env python3
"""One-time structural migration of Paper A's transfer artefacts from schema 3 to schema 4.

Round-10 P0-1/P1-2/P1-3 change what the artefacts must SAY about themselves, not what they compute:

  * the resampling design's free-text ``estimand`` sentence becomes a typed estimand object whose
    direction is derived from primitives and re-derived on validation (P1-2);
  * the design gains a typed ``inferential_status`` object declaring which decisions the analysis
    can make — all of them ``false``, with no practical margin, because that is what a
    fixed-predictor clustered percentile sensitivity range supports (P0-1);
  * every interval record gains exact full-precision zero-contact flags, and its ambiguous
    ``display.touches_zero`` becomes ``display.contains_zero_rounded`` (P1-3).

Regenerating the artefacts through ``--write`` would re-solve every PDE — roughly a quarter of an
hour of numerical work whose results are not in question, and whose Monte Carlo bounds would move in
the last displayed digit for reasons unrelated to this remediation. So the migration is done
DETERMINISTICALLY and structurally:

  * interval records are rebuilt by the canonical constructor from their own archived
    full-precision bounds, so no bound moves and every derived field is what those bounds imply;
  * the resampling design is rebuilt from the SOURCE CSV through the contract's own grouping
    functions, and the migration ABORTS unless the rebuilt membership is identical, cluster for
    cluster, to the committed one;
  * the renamed display flags are carried over by name, with their values recomputed;
  * nothing else is touched.

The migration then runs the full artefact check and the frozen numerical invariants, and refuses to
leave a changed tree if either fails.

    python tools/paper_a_migrate_schema4.py            # dry run
    python tools/paper_a_migrate_schema4.py --write    # apply

It is **idempotent**, and that is a property worth having rather than an accident: every field it
writes is derived deterministically from the archived bounds or from the source CSV, so re-running it
on an already-migrated tree must produce no diff. That makes it a re-verification of the migration
rather than a one-shot script whose claim to have preserved the numbers can never be checked again.
Running it on a tree where a structural field has been hand-edited restores the derived value.

It is deliberately NOT a general migration facility: a future schema change should get its own
script, describing its own field-by-field intent.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from puckworks.paper_a import transfer_contract as TC  # noqa: E402

RESOURCE = _REPO / "docs" / "paper1_resource"
ENDPOINT_JSON = RESOURCE / "PAPER_A_ENDPOINT_PROPAGATION.json"
CORPUS_JSON = RESOURCE / "PAPER_A_TRANSFER_CORPUS_CONTRACTS.json"
LOSS_JSON = RESOURCE / "PAPER_A_COMPARATOR_LOSS_ROBUSTNESS.json"
ARTIFACTS = (ENDPOINT_JSON, CORPUS_JSON, LOSS_JSON)

FROM_SCHEMA = 3
TO_SCHEMA = 4

#: Flat aliases whose NAME carried the ambiguity the interval field carried (round-10 P1-3): each
#: describes the DISPLAYED range rounding onto zero, not exact contact with it.
_RENAMED_FLAGS = {
    "within_variety_display_touches_zero": "within_variety_display_contains_zero_rounded",
    "display_touches_zero": "display_contains_zero_rounded",
    "range_display_touches_zero_stable": "range_display_contains_zero_rounded_stable",
}


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _dump(obj: dict) -> str:
    """Same serialisation as the artefact writer, with NaN/Infinity refused outright."""
    return json.dumps(obj, indent=1, ensure_ascii=False, sort_keys=False, allow_nan=False) + "\n"


def design_records_from_source() -> list[dict]:
    """Per-observation records in the producer's shape, built from the SOURCE data only.

    The cluster design depends on corpus membership and nothing else — no endpoint, no solve, no
    resampling — which is why the producer builds it once for the whole sweep. It can therefore be
    rebuilt here from the source CSV without re-running anything numerical.
    """
    from puckworks import data as d

    manifest = TC.build_transfer_corpus_manifest(d.angeloni_bioactives(), include_off_grid=True)
    out = []
    for r in manifest["records"]:
        for solute in r["solutes"]:
            out.append(dict(group="%s:%s" % (r["variety"], solute), variety=r["variety"],
                            solute=solute, sample=r["sample_id"], grind=r["grind"],
                            T=r["temperature_degC"], p=r["pressure_bar"], delta=0.0))
    return out


def _migrate_intervals(node, problems: list[str], path: str = "") -> None:
    """Rebuild every interval record in place from its own archived bounds."""
    if isinstance(node, dict):
        if "full_precision_pp" in node and "display" in node:
            fp = node["full_precision_pp"]
            digits = int(node["display"].get("digits", TC.PP_DIGITS))
            try:
                fresh = TC.interval_record(fp["lower"], fp["upper"], digits)
            except (KeyError, TypeError, ValueError) as exc:
                problems.append("%s: cannot rebuild interval: %s" % (path, exc))
                return
            if fresh["full_precision_pp"] != {"lower": float(fp["lower"]),
                                              "upper": float(fp["upper"])}:
                problems.append("%s: rebuilding moved a full-precision bound" % path)
                return
            node.clear()
            node.update(fresh)
            return
        for key, value in list(node.items()):
            _migrate_intervals(value, problems, "%s.%s" % (path, key))
    elif isinstance(node, list):
        for i, value in enumerate(node):
            _migrate_intervals(value, problems, "%s[%d]" % (path, i))


def _rename_flags(node) -> None:
    """Apply the display-flag renames wherever they occur, preserving field order."""
    if isinstance(node, dict):
        for old, new in _RENAMED_FLAGS.items():
            if old in node:
                rebuilt = {(new if k == old else k): v for k, v in node.items()}
                node.clear()
                node.update(rebuilt)
        for value in node.values():
            _rename_flags(value)
    elif isinstance(node, list):
        for value in node:
            _rename_flags(value)


def migrate() -> tuple[dict, list[str]]:
    """Return ``({path: migrated_artifact}, problems)``. Never writes."""
    problems: list[str] = []
    loaded = {}
    for path in ARTIFACTS:
        if not path.exists():
            problems.append("missing artefact %s" % path.relative_to(_REPO))
            continue
        loaded[path] = _load(path)
    if problems:
        return {}, problems

    for path, art in loaded.items():
        found = int(art.get("schema_version", 0))
        if found not in (FROM_SCHEMA, TO_SCHEMA):
            problems.append("%s is schema %r; this migration understands %d (to migrate) and %d "
                            "(to re-verify)" % (path.name, art.get("schema_version"),
                                                FROM_SCHEMA, TO_SCHEMA))
    if problems:
        return {}, problems

    for path, art in loaded.items():
        _migrate_intervals(art, problems, path.name)
        _rename_flags(art)
        art["schema_version"] = TO_SCHEMA

    # ── the resampling design, rebuilt from source and required to be the SAME partition ────────
    ep = loaded[ENDPOINT_JSON]
    committed = ep.get("resampling_design") or {}
    rebuilt = TC.resampling_design(design_records_from_source())
    for name in TC.SCHEME_ORDER:
        was = ((committed.get("schemes") or {}).get(name) or {}).get("membership")
        now = rebuilt["schemes"][name]["membership"]
        if was != now:
            problems.append(
                "scheme %r: the design rebuilt from the source CSV is not the committed partition. "
                "This migration is structural and must not change membership — adjudicate the "
                "difference before writing anything" % name)
    if not problems:
        ep["resampling_design"] = rebuilt

    return loaded, problems


def write() -> list[str]:
    """Migrate, write atomically, then refuse to leave a tree that fails its own checks."""
    migrated, problems = migrate()
    if problems:
        return problems

    backups = {p: p.read_text(encoding="utf-8") for p in migrated}
    for path, art in migrated.items():
        path.write_text(_dump(art), encoding="utf-8")

    from tools import paper_a_numerical_invariants as NI
    from tools import paper_a_transfer_artifacts as ART

    problems = ["artefact check: %s" % p for p in ART.check()]
    # The frozen invariants must be unchanged except for ONE field: the estimand's identity, which
    # was recorded pre-migration through a shim as `pre_schema4_free_text` because a v3 artefact has
    # no typed estimand to name. That difference is the migration's whole point. Any other
    # difference is a moved number and rolls the tree back.
    for problem in NI._diff(json.loads(NI.INVARIANTS.read_text(encoding="utf-8")),
                            NI.extract(), "invariants"):
        if problem.startswith("invariants.estimand."):
            print("    expected identity change: %s" % problem)
            continue
        problems.append("numerical invariants: %s" % problem)
    if problems:
        for path, text in backups.items():
            path.write_text(text, encoding="utf-8")
        return ["the migrated artefacts failed validation; the tree was rolled back"] + problems
    return []


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--write", action="store_true", help="apply the migration (default: dry run)")
    args = ap.parse_args(argv)

    if args.write:
        problems = write()
        verb = "write"
    else:
        _migrated, problems = migrate()
        verb = "dry run"
    if problems:
        print("Paper A schema-4 migration FAILED (%s):" % verb, file=sys.stderr)
        for p in problems:
            print("  - %s" % p, file=sys.stderr)
        return 1
    print("Paper A schema-4 migration OK (%s): 3 artefacts, no bound moved." % verb)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
