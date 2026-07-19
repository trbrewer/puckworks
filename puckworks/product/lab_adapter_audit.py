"""Adapter-readiness audit for a SECOND Guided Pull Laboratory common-scenario lens (PV-19B Phase 4).

A deterministic, evidence-based audit of the extraction-stage candidates against the effective common
scenario. A model may be admitted as a common-scenario lens ONLY when every required input has a source,
every unit/reference-basis conversion is explicit and tested, the grinder input needs no universal dial
mapping, the scenario lies inside the model's validity range, rights are clear, runtime is acceptable,
and the authoritative producer can be reused. Otherwise the model keeps an honest disposition — no
adapter is invented, and no incompatible outputs are overlaid.

Finite decisions: READY_FOR_BOUNDED_ADAPTER, ADAPTER_REQUIRES_TESTED_CONVERSION, OUTSIDE_COMMON_DOMAIN,
OUTPUTS_NOT_COMPARABLE, RIGHTS_BLOCKED, RUNTIME_BLOCKED, INSUFFICIENT_PROVENANCE.
"""
from __future__ import annotations

import json

DECISIONS = ("READY_FOR_BOUNDED_ADAPTER", "ADAPTER_REQUIRES_TESTED_CONVERSION", "OUTSIDE_COMMON_DOMAIN",
             "OUTPUTS_NOT_COMPARABLE", "RIGHTS_BLOCKED", "RUNTIME_BLOCKED", "INSUFFICIENT_PROVENANCE")

# Per-candidate assessment against the common scenario (facts sourced from the cards / registry /
# README). Each records the specific blocker; none is invented compatibility.
_CANDIDATES = {
    "pannusch2024.solver": {
        "decision": "ADAPTER_REQUIRES_TESTED_CONVERSION",
        "temperature_flow": "consumed (T 80-98 C, Q 1-3 mL/s) — overlaps the scenario",
        "grind_input": "center-grind (EK43 1.7) assumption; NOT a portable EK43->size mapping",
        "concentration_reference_basis": "per-species concentrations vs Cameron single-pool EY/TDS on a "
                                         "bed-volume basis — a justified per-species->pool collapse AND "
                                         "a reference-basis reconciliation are both required and untested",
        "output_definition": "multi-species (caffeine/trigonelline/CGA) — not the single pool Cameron reports",
        "rights_note": "post-fit reconstruction; published article",
        "runtime": "measure before admitting (potentially batch-only)",
        "reason": "outputs are per-species on a different reference basis; comparison needs a tested "
                  "inventory-conserving conversion + a justified collapse — do NOT overlay yet",
    },
    "romancorrochano2017.extraction": {
        "decision": "OUTPUTS_NOT_COMPARABLE",
        "temperature_flow": "T-corrected diffusion; flow trend only",
        "grind_input": "grain-scale microstructural diffusion; no dial mapping",
        "concentration_reference_basis": "supplies a flow *trend*, not absolute yield on Cameron's basis",
        "output_definition": "relative extraction trend (sign/compatibility evidence), not absolute EY/TDS",
        "rights_note": "published article",
        "runtime": "fast",
        "reason": "the model provides a trend, not an absolute EY/TDS on a comparable basis; overlaying "
                  "it as a second EY/TDS lens would be an evidence upgrade",
    },
    "mo2023_2.coupled_bed": {
        "decision": "ADAPTER_REQUIRES_TESTED_CONVERSION",
        "temperature_flow": "fixed flow; type-M regime",
        "grind_input": "fine/coarse families; no dial mapping",
        "concentration_reference_basis": "per bed-depth cell; absolute yield needs ONE inventory scale — "
                                         "an inventory-conserving conversion to Cameron's bed-volume basis "
                                         "is required and untested",
        "output_definition": "bed-depth-resolved; cup mass < ~30 g validity",
        "rights_note": "published article",
        "runtime": "measure before admitting",
        "reason": "per-bed-cell concentration needs a tested inventory scale before any overlay",
    },
    "grudeva2025.reduced": {
        "decision": "RIGHTS_BLOCKED",
        "temperature_flow": "n/a",
        "grind_input": "n/a",
        "concentration_reference_basis": "grain-volume incl. internal pores — differs from Cameron",
        "output_definition": "n/a",
        "rights_note": "self-documented port of unlicensed upstream code (issue #73)",
        "runtime": "n/a",
        "reason": "rights unresolved (#73); excluded from lens consideration entirely",
    },
}


def _extraction_candidates():
    import puckworks
    return [c.name for c in puckworks.components()
            if c.stage == "extraction" and c.execution_role == "runtime"
            and c.name != "cameron2020.extraction_bdf"]


def build_audit() -> dict:
    import puckworks
    ev = {c.name: {"evidence_strength": c.evidence_strength, "validity_range": c.valid_range}
          for c in puckworks.components()}
    rows = []
    from puckworks.product import reference_basis as rb
    for name in sorted(_extraction_candidates()):
        a = dict(_CANDIDATES.get(name, {"decision": "INSUFFICIENT_PROVENANCE",
                                        "reason": "no assessment on record; treat conservatively"}))
        a["component_id"] = name
        a["evidence_strength"] = ev.get(name, {}).get("evidence_strength")
        a["validity_range"] = ev.get(name, {}).get("validity_range")
        # rights come from the centralized registry (never a hard-coded 'clear' in this module)
        from puckworks import rights as _rights
        rec = _rights.rights_record(name)
        a["code_rights_state"] = rec.code_rights_state
        a["data_rights_state"] = rec.data_rights_state
        a["output_redistribution_state"] = rec.output_redistribution_state
        a["public_execution_allowed"] = _rights.may_execute_in_public_batch(name).allowed
        # bind the prose decision to the machine-checked typed basis + admissibility (they cannot disagree)
        readiness = rb.adapter_readiness(name)
        a["quantity_basis"] = readiness["quantity_basis"]
        a["admissible_as_second_lens"] = readiness["admissible_as_second_lens"]
        assert a["decision"] in DECISIONS
        assert not (a["admissible_as_second_lens"] and a["decision"] != "READY_FOR_BOUNDED_ADAPTER")
        rows.append(a)
    rows.sort(key=lambda r: r["component_id"])
    ready = [r["component_id"] for r in rows if r["decision"] == "READY_FOR_BOUNDED_ADAPTER"]
    counts = {}
    for r in rows:
        counts[r["decision"]] = counts.get(r["decision"], 0) + 1
    return {
        "report": "puckworks-lab-adapter-readiness",
        "common_scenario_lens": "cameron2020.extraction_bdf (bed-volume single-pool EY/TDS)",
        "candidates": rows,
        "decisions": dict(sorted(counts.items())),
        "ready_for_bounded_adapter": ready,
        "conclusion": ("No extraction candidate is ready for a bounded common-scenario adapter without an "
                       "invented conversion. Each needs a tested reference-volume / inventory conversion "
                       "or is rights-blocked, so NO second lens is added; the honest dispositions and this "
                       "readiness report are the deliverable."
                       if not ready else f"Ready: {', '.join(ready)}"),
        "boundaries": ["no universal grinder-dial conversion", "no incompatible concentration-basis "
                       "overlay", "no averaging / ensembling of competing mechanisms",
                       "model agreement is not validation"],
    }


def canonical_json(report: dict) -> str:
    return json.dumps(report, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def render_markdown(report: dict) -> str:
    lines = ["# Guided Pull Laboratory — second-lens adapter-readiness audit", "",
             f"_Common-scenario lens today: **{report['common_scenario_lens']}**._", "",
             "## Decisions", ""]
    for k, v in report["decisions"].items():
        lines.append(f"- `{k}`: {v}")
    lines += ["", "## Candidates", ""]
    for r in report["candidates"]:
        lines.append(f"### `{r['component_id']}` — **{r['decision']}**")
        lines.append(f"- quantity basis (typed): `{r.get('quantity_basis')}` · admissible as second "
                     f"lens: {r.get('admissible_as_second_lens')}")
        lines.append(f"- reference basis: {r.get('concentration_reference_basis')}")
        lines.append(f"- output definition: {r.get('output_definition')}")
        lines.append(f"- grind input: {r.get('grind_input')}")
        lines.append(f"- temperature/flow: {r.get('temperature_flow')}")
        lines.append(f"- rights (code/data/output): `{r.get('code_rights_state')}` / "
                     f"`{r.get('data_rights_state')}` / `{r.get('output_redistribution_state')}` "
                     f"(public execution allowed: {r.get('public_execution_allowed')}) — "
                     f"{r.get('rights_note','')}")
        lines.append(f"- runtime: {r.get('runtime')} · evidence: {r.get('evidence_strength')}")
        lines.append(f"- **reason:** {r.get('reason')}")
        lines.append("")
    lines += ["## Conclusion", "", report["conclusion"], "",
              "## Boundaries", ""] + [f"- {b}" for b in report["boundaries"]] + [""]
    return "\n".join(lines)


def main(argv=None) -> int:
    import argparse
    import sys
    ap = argparse.ArgumentParser(prog="puckworks.product.lab_adapter_audit", description=__doc__)
    ap.add_argument("--format", choices=["md", "json"], default="md")
    a = ap.parse_args(argv)
    report = build_audit()
    sys.stdout.write(canonical_json(report) if a.format == "json" else render_markdown(report))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
