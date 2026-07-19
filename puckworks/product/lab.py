"""Guided Pull Laboratory (PV-19B): expose the full component registry, run the compatible subset as
independent model lenses.

Two modes, kept scrupulously distinct:

* **Common-scenario model lenses** — one bounded espresso scenario is mapped into the *compatible*
  models; each runs independently through its existing authoritative producer. Only `cameron2020.
  extraction_bdf` is executed as the common-scenario lens today (via `puckworks.product.simulate_pull`);
  every competing/other component gets an honest disposition rather than an invented overlay.
* **Component reference suite** — executable components' native reference cases (registry visibility),
  never presented as predictions of the common shot.

This module **duplicates no model equation**: it calls the existing `simulate_pull` producer and the
registry. It never sums or averages competing mechanisms, never maps a grinder dial to a universal
particle size, never overlays incompatible concentration reference volumes, and never upgrades an
evidence label. Serialization is deterministic and carries no wall-clock field.

CLI::

    python -m puckworks.product.lab matrix   --format md|json
    python -m puckworks.product.lab compare  --format md|json
"""
from __future__ import annotations

import argparse
import json
import sys

SCHEMA_VERSION = 2                     # product-facing comparison contract, distinct from PullRun v1
_PRESET = "pv19_named"

# Finite coverage vocabulary (PV-19B). Every registered component receives exactly one.
DISPOSITIONS = (
    "COMMON_SCENARIO_READY",
    "COMMON_SCENARIO_WITH_VERIFIED_ADAPTER",
    "NATIVE_REFERENCE_ONLY",
    "SUPPORTING_STAGE_LENS",
    "CALIBRATION_OR_CLOSURE",
    "ADAPTER_REQUIRED",
    "OUTSIDE_SCENARIO_DOMAIN",
    "RIGHTS_BLOCKED",
    "NOT_EXECUTABLE",
    "SKIPPED_OPTIONAL_DEPENDENCY",
    "FAILED",                          # reserved for an execution that ERRORED, never for "unsupported"
)

WHAT_THIS_DOES_NOT_PROVE = [
    "Model agreement is not validation; these are independent lenses, not a validated digital twin.",
    "Competing mechanisms are never summed or averaged; overlaying two models is not an ensemble.",
    "A grinder dial is not a universal particle size; no dial->size conversion is applied.",
    "Concentrations on different reference volumes (bed-volume vs grain-volume) are not overlaid; such "
    "lenses are marked ADAPTER_REQUIRED until an inventory-conserving conversion is tested.",
    "The common scenario is not a best recipe and predicts no flavor or sensory quality.",
    "Native reference-suite results are each a component's OWN reference case, not a prediction of the "
    "common shot.",
]


def _components():
    import puckworks
    return list(puckworks.components())


def _run_common_scenario() -> dict:
    """Execute the existing authoritative producer for the common scenario (cameron2020.extraction_bdf).
    Returns the PullRun dict. Raises only if the producer itself errors."""
    import puckworks.product as prod
    recipe, config = prod.load_pull_preset(_PRESET)
    return prod.pull_run_to_dict(prod.simulate_pull(recipe, config))


def classify(comp, cov_disposition: str | None) -> tuple:
    """Map a registered component to exactly one PV-19B disposition + a reason. Uses the registry
    metadata and the existing Guided-Pull coverage disposition; never invents compatibility."""
    role = getattr(comp, "execution_role", "")
    kind = getattr(comp, "kind", "")
    stage = getattr(comp, "stage", "")
    if cov_disposition == "executed_primary":
        return "COMMON_SCENARIO_READY", "executed as the common-scenario extraction lens (primary chain)"
    if cov_disposition == "excluded_optional_dependency":
        return ("SKIPPED_OPTIONAL_DEPENDENCY",
                "optional accelerator/GPU dependency (e.g. taichi); never part of the base install and "
                "never counted as a pass")
    if role == "calibration" or kind == "calibration":
        return "CALIBRATION_OR_CLOSURE", "supplies calibration/closure inputs, not a standalone prediction"
    if kind in ("reference", "synthesis") or "reference" in (getattr(comp, "notes", "") or "").lower():
        return "NATIVE_REFERENCE_ONLY", "pore-scale / synthesis reference solver; native reference case only"
    # available_as_separate_lens (or anything else executable but not the primary chain)
    if stage == "extraction":
        return ("ADAPTER_REQUIRED",
                "competing extraction mechanism on a possibly different observable / concentration "
                "reference volume; needs a tested inventory-conserving adapter before any overlay")
    if stage in ("bed_dynamics", "flow", "infiltration", "machine"):
        return ("SUPPORTING_STAGE_LENS",
                f"{stage}-stage model producing a different observable; an independent lens, not overlaid "
                "on the extraction scenario")
    return "NATIVE_REFERENCE_ONLY", "kept as an independent native reference lens"


def build_matrix(run: dict | None = None) -> list:
    """The deterministic all-component coverage matrix. Every component -> exactly one disposition."""
    if run is None:
        run = _run_common_scenario()
    cov = {c["component_id"]: c for c in run.get("coverage", [])}
    rows = []
    for comp in _components():
        cd = cov.get(comp.name, {})
        disp, reason = classify(comp, cd.get("disposition"))
        rows.append({
            "component_id": comp.name,
            "stage": comp.stage,
            "kind": comp.kind,
            "execution_role": comp.execution_role,
            "module": comp.module,
            "provenance_class": comp.provenance_class,
            "evidence_strength": comp.evidence_strength,
            "n_gates": len(comp.gates),
            "executable": comp.execution_role in ("runtime", "calibration"),
            "executed_in_common_scenario": bool(cd.get("executed")),
            "disposition": disp,
            "reason": reason,
            "validity_range": comp.valid_range,
        })
    rows.sort(key=lambda r: r["component_id"])       # stable, import-order independent
    return rows


def _lens_result_from_run(run: dict) -> dict:
    """Wrap the executed primary lens (cameron2020.extraction_bdf) as a LensResult with evidence."""
    obs = run.get("final_observables", {})
    lens_observables = []
    for key, o in sorted(obs.items()):
        if not isinstance(o, dict):
            continue
        lens_observables.append({
            "name": key,
            "value": o.get("value"),
            "unit": o.get("unit"),
            "role": ("unsupported" if o.get("status") == "unavailable" else "derived"),
            "note": o.get("note") or o.get("reason") or "",
        })
    traces = []
    for t in run.get("traces", []):
        traces.append({
            "trace_id": t.get("trace_id"),
            "observable": t.get("axis_label"),
            "axis_unit": t.get("axis_unit"),
            "evidence_badge": t.get("evidence_badge"),
            "evidence_strength": t.get("evidence_strength"),
            "fidelity_ceiling": t.get("fidelity_ceiling"),
            "n_points": len(t.get("axis_values", [])),
        })
    return {
        "component_id": "cameron2020.extraction_bdf",
        "adapter": "puckworks.product.simulate_pull(pv19_named)",
        "status": "executed",
        "disposition": "COMMON_SCENARIO_READY",
        "observables": lens_observables,
        "traces": traces,
        "domain_findings": run.get("domain_findings", []),
        "warnings": run.get("warnings", []),
        "evidence_note": "executed via the existing authoritative producer; no equation is re-implemented",
    }


def _reference_suite(matrix: list, run: dict) -> list:
    """Native reference cases. cameron2020 has an executed native reference (the primary run itself);
    every other executable component is REFERENCE_ONLY (native runner not yet wired) — a skip is never
    a pass. Deterministic."""
    out = []
    for row in matrix:
        if not row["executable"]:
            out.append({"component_id": row["component_id"], "status": "not_executable",
                        "note": "not a runtime/calibration component"})
            continue
        if row["disposition"] == "SKIPPED_OPTIONAL_DEPENDENCY":
            out.append({"component_id": row["component_id"], "status": "SKIPPED_OPTIONAL_DEPENDENCY",
                        "note": "optional accelerator dependency; excluded from the base install"})
            continue
        if row["component_id"] == "cameron2020.extraction_bdf":
            out.append({"component_id": row["component_id"], "status": "executed_native_reference",
                        "label": "This is the component's native reference case, not the common Guided "
                                 "Pull scenario.",
                        "note": "executed via simulate_pull(pv19_named)"})
            continue
        out.append({"component_id": row["component_id"], "status": "REFERENCE_ONLY",
                    "label": "This is the component's native reference case, not the common Guided Pull "
                             "scenario.",
                    "note": "native reference runner not yet wired; registered + gated in the registry"})
    out.sort(key=lambda r: r["component_id"])
    return out


def build_comparison(run: dict | None = None) -> dict:
    """The full deterministic ComparisonRun (schema v2). No wall-clock in the canonical content."""
    if run is None:
        run = _run_common_scenario()
    matrix = build_matrix(run)
    by_disp: dict[str, int] = {}
    for r in matrix:
        by_disp[r["disposition"]] = by_disp.get(r["disposition"], 0) + 1
    lens = _lens_result_from_run(run)
    scenario = {
        "scenario_id": _PRESET,
        "title": "Guided Pull Laboratory common scenario (bounded, one machine/coffee)",
        "recipe": run.get("recipe", {}),
        "source": "puckworks.product.load_pull_preset('pv19_named') — a fixed reference recipe",
    }
    return {
        "schema_version": SCHEMA_VERSION,
        "report": "puckworks-guided-pull-laboratory",
        "provenance": {"source_commit": run.get("source_commit"),
                       "package_version": run.get("package_version"),
                       "pull_run_id": run.get("run_id"),
                       "pull_schema_version": run.get("schema_version")},
        "scenario": scenario,
        "counts": {
            "components": len(matrix),
            "executed_common_scenario_lenses": 1,
            "dispositions": dict(sorted(by_disp.items())),
        },
        "executed_lenses": [lens],
        "excluded_or_dispositioned": [
            {"component_id": r["component_id"], "disposition": r["disposition"], "reason": r["reason"]}
            for r in matrix if r["disposition"] != "COMMON_SCENARIO_READY"
        ],
        "component_matrix": matrix,
        "component_reference_suite": _reference_suite(matrix, run),
        "what_this_does_not_prove": WHAT_THIS_DOES_NOT_PROVE,
        "fidelity_ceiling": "One bounded scenario on one machine/coffee; one executed extraction lens; "
                            "the rest are independent lenses / native references. Not a validated "
                            "multi-model simulation, not a digital twin, not a best recipe.",
    }


def _canonical_no_wallclock(report: dict) -> dict:
    """Return a copy suitable for canonical hashing: drop the per-checkout source_commit (provenance,
    not a scientific value) so the hash is stable across commits; keep everything else."""
    r = json.loads(json.dumps(report))
    r.get("provenance", {}).pop("source_commit", None)
    r.get("provenance", {}).pop("package_version", None)
    return r


def canonical_json(report: dict) -> str:
    return json.dumps(_canonical_no_wallclock(report), indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def render_markdown(report: dict) -> str:
    c = report["counts"]
    lines = [
        "# Guided Pull Laboratory — model-lens comparison",
        "",
        "_Independent model lenses over one bounded scenario, plus a component reference suite. "
        "**Not** a validated digital twin; competing mechanisms are never summed or averaged._",
        "",
        f"- registered components: **{c['components']}** · executed common-scenario lenses: "
        f"**{c['executed_common_scenario_lenses']}**",
        "",
        "## Coverage by disposition",
        "",
    ]
    for k, v in c["dispositions"].items():
        lines.append(f"- `{k}`: {v}")
    lines += ["", "## Executed common-scenario lens", ""]
    for lens in report["executed_lenses"]:
        lines.append(f"### `{lens['component_id']}` — {lens['status']} ({lens['adapter']})")
        lines.append("")
        lines.append("| observable | value | unit | role |")
        lines.append("|---|---|---|---|")
        for o in lens["observables"]:
            lines.append(f"| {o['name']} | {o['value']} | {o['unit'] or ''} | {o['role']} |")
        lines.append("")
    lines += ["## Excluded / dispositioned components (honest, not hidden)", ""]
    for e in report["excluded_or_dispositioned"]:
        lines.append(f"- `{e['component_id']}` — **{e['disposition']}**: {e['reason']}")
    lines += ["", "## Component reference suite", "",
              "_Each is the component's OWN native reference case, not the common scenario._", ""]
    for r in report["component_reference_suite"]:
        lines.append(f"- `{r['component_id']}` — {r['status']}")
    lines += ["", "## What this does not prove", ""]
    lines += [f"- {s}" for s in report["what_this_does_not_prove"]]
    lines += ["", f"**Fidelity ceiling.** {report['fidelity_ceiling']}", ""]
    return "\n".join(lines)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="puckworks.product.lab", description=__doc__)
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name in ("matrix", "compare"):
        s = sub.add_parser(name)
        s.add_argument("--format", choices=["md", "json"], default="md")
        s.add_argument("--out", default=None)
    args = ap.parse_args(argv)
    run = _run_common_scenario()
    if args.cmd == "matrix":
        matrix = build_matrix(run)
        text = (json.dumps(matrix, indent=2, sort_keys=True) + "\n" if args.format == "json"
                else "\n".join(f"{r['component_id']:34} {r['disposition']:32} {r['reason'][:60]}"
                               for r in matrix) + "\n")
    else:
        report = build_comparison(run)
        text = canonical_json(report) if args.format == "json" else render_markdown(report)
    if args.out:
        from pathlib import Path
        Path(args.out).write_text(text, encoding="utf-8")
        print(f"wrote {args.out}")
    else:
        sys.stdout.write(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
