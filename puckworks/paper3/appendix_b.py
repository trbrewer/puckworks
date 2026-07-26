"""GENERATE Appendix B (the machine-readable claim record) from the real schema.

Paper 3 review P0-10: Appendix B was a hand-written YAML sketch. It simultaneously UNDERSTATED the
public object -- omitting headline, plain-language finding, uncertainty/sensitivity, practical
implication and full provenance, all of which §6.4 calls load-bearing -- and OVERSTATED its evidence
semantics, presenting a single `evidence_strength` plus a badge as if that were the multi-field
evidence model of §5.

An appendix advertised as machine-readable must not be maintained as parallel prose. This module
emits it from `puckworks.public.schema.PublicClaim` itself, so the appendix cannot drift from the
object the release actually exports, and marks each field mandatory / optional / derived.

    python -m puckworks.paper3.appendix_b            # print
    python -m puckworks.paper3.appendix_b --write    # write into the manuscript
    python -m puckworks.paper3.appendix_b --verify   # exit 1 if the manuscript is stale
"""
from __future__ import annotations

import dataclasses as dc
import pathlib

from puckworks.public import schema as S

REPO = pathlib.Path(__file__).resolve().parents[2]
MANUSCRIPT = REPO / "docs" / "PAPER_3_PUCKWORKS_DRAFT.md"
_BEGIN = "<!-- appendix-b:begin -->"
_END = "<!-- appendix-b:end -->"

#: Fields whose value is COMPUTED from other fields or from the export process, never authored.
DERIVED_FIELDS = {
    "badge": "derived from the authored evidence fields (§5); never authored independently",
    "source_commit": "DEPRECATED alias of generated_from_commit",
    "generated_from_commit": "stamped at first export; immutable thereafter",
    "last_verified_against_commit": "stamped at every successful verification; mutable",
}

#: Fields that carry a list/mapping of repeatable entries.
REPEATABLE_FIELDS = {"numeric_result", "units", "components", "dataset_manifest_ids"}

_FIELD_NOTES = {
    "claim_id": "stable identifier; the join key across manuscript, site and evidence graph",
    "public_question": "the scientific question in lay terms",
    "headline": "one-line answer",
    "plain_language_finding": "interpretation for a non-specialist reader",
    "numeric_result": "producer-generated values; NEVER hand-entered",
    "units": "one unit per numeric key -- a value without a unit is rejected",
    "uncertainty_or_sensitivity": "what the number is sensitive to, or its spread",
    "evidence_strength": "PUBLIC lay relation, mapped from the registry relation via "
                         "`REGISTRY_TO_PUBLIC`; a coarser vocabulary, not the registry value",
    "components": "registered component / harness identifiers used",
    "dataset_manifest_ids": "rows that MUST exist in data/MANIFEST.csv",
    "validity_range": "explicit domain of applicability",
    "primary_caveat": "the limitation a reader must carry away",
    "practical_implication": "what it does and does not license in practice",
    "reproduction": "one-line command that regenerates the value",
    "producer": "executable identity: module, function, result path, kwargs, cost flag",
    "compares_grinder_dials": "if true the caveat MUST warn that dial spaces are non-portable",
}


def _obligation(f):
    if f.name in DERIVED_FIELDS:
        return "derived"
    optional = not (f.default is dc.MISSING and f.default_factory is dc.MISSING)
    base = "optional" if optional else "mandatory"
    return f"{base}, repeatable" if f.name in REPEATABLE_FIELDS else base


_TYPE_NAMES = {"str": "string", "str | None": "string (optional)", "dict": "mapping",
               "list": "list", "bool": "boolean", "Producer": "Producer"}


def _type_name(f):
    """Map the annotation to a reader-facing type name. Uses an exact-match table rather than
    chained str.replace, which previously turned "str | None" into "stringing?"."""
    t = f.type if isinstance(f.type, str) else getattr(f.type, "__name__", str(f.type))
    return _TYPE_NAMES.get(str(t).strip(), str(t).strip())


def _example(claim, keep=6):
    """A REAL claim rendered compactly -- not an invented illustration."""
    lines = [f"claim_id: {claim.claim_id}",
             f"headline: {claim.headline[:96]}",
             f"evidence_strength: {claim.evidence_strength}",
             f"badge: {claim.badge}",
             "numeric_result:"]
    for k, v in list(claim.numeric_result.items())[:keep]:
        lines.append(f"  {k}: {v}   # unit: {claim.units.get(k, 'MISSING')}")
    lines += ["producer:",
              f"  module: {claim.producer.module}",
              f"  function: {claim.producer.function}",
              f"  slow: {claim.producer.slow}",
              f"components: {list(claim.components)}",
              f"datasets: {list(claim.dataset_manifest_ids)}",
              f"primary_caveat: {claim.primary_caveat[:96]}"]
    return "\n".join(lines)


def render():
    from puckworks.public.claims import PUBLIC_CLAIMS
    by_id = {c.claim_id: c for c in PUBLIC_CLAIMS}
    passing = by_id.get("PV-01") or PUBLIC_CLAIMS[0]
    negative = next((c for c in PUBLIC_CLAIMS if "negative" in c.evidence_strength.lower()),
                    PUBLIC_CLAIMS[-1])

    out = [_BEGIN,
           "## Appendix B. Machine-readable claim record (generated)",
           "",
           "*Generated from `puckworks.public.schema.PublicClaim` by "
           "`python -m puckworks.paper3.appendix_b --write`; a CI check fails if this section "
           "drifts from the schema the release exports. Do not hand-edit.*",
           "",
           "Every manuscript-facing quantitative claim is exportable as the record below. Fields are "
           "marked **mandatory**, **optional**, **repeatable** or **derived**; a derived field is "
           "computed from the others or stamped by the export process and must never be authored "
           "independently, so it cannot be cited as separate corroboration.",
           "",
           "| field | type | obligation | meaning |",
           "|---|---|---|---|"]
    for f in dc.fields(S.PublicClaim):
        note = _FIELD_NOTES.get(f.name) or DERIVED_FIELDS.get(f.name, "")
        out.append(f"| `{f.name}` | {_type_name(f)} | {_obligation(f)} | {note} |")

    out += ["",
            "**Commit provenance.** `generated_from_commit` is immutable — the commit the payload "
            "was produced at — while `last_verified_against_commit` moves on every successful "
            "re-verification. A snapshot may therefore verify at a later commit while still "
            "declaring the earlier commit it was generated from; those are different facts and are "
            "recorded separately. `source_commit` is retained only as a deprecated alias.",
            "",
            "**Evidence semantics.** `evidence_strength` here is the *public, lay* relation, mapped "
            "from the registry relation by `puckworks.public.schema.REGISTRY_TO_PUBLIC`. It is one "
            "field of the evidence model (§5), not the whole of it: outcome, artifact role and "
            "scope are recorded alongside it, and the badge is derived from them.",
            "",
            "**Example — a supported claim.**",
            "", "```yaml", _example(passing), "```", "",
            "**Example — a negative outcome.** Negative results are first-class: a failed check is "
            "a failed *outcome* on some relation, never a relation of its own.",
            "", "```yaml", _example(negative), "```", "",
            "A graphic or abstract number without such a record should be treated as untracked.",
            _END]
    return "\n".join(out)


def _splice(text, block):
    if _BEGIN in text and _END in text:
        pre = text.split(_BEGIN)[0]
        post = text.split(_END, 1)[1]
        return pre + block + post
    old = text.split("## Appendix B. Minimal machine-readable claim record")
    if len(old) == 2:
        tail = old[1].split("## References", 1)
        return old[0] + block + "\n\n## References" + (tail[1] if len(tail) > 1 else "")
    raise SystemExit("could not locate Appendix B in the manuscript")


def write():
    MANUSCRIPT.write_text(_splice(MANUSCRIPT.read_text(encoding="utf-8"), render()),
                          encoding="utf-8")
    return MANUSCRIPT


def verify():
    """Return '' when the manuscript's Appendix B matches the generated block."""
    text = MANUSCRIPT.read_text(encoding="utf-8")
    if _BEGIN not in text or _END not in text:
        return "Appendix B is not generated (missing markers) — run --write"
    cur = _BEGIN + text.split(_BEGIN, 1)[1].split(_END, 1)[0] + _END
    return "" if cur.strip() == render().strip() else "Appendix B is stale — run --write"


if __name__ == "__main__":  # pragma: no cover
    import sys
    if "--write" in sys.argv:
        print("wrote", write())
    elif "--verify" in sys.argv:
        p = verify()
        print(p or "Appendix B is current")
        sys.exit(1 if p else 0)
    else:
        print(render())
