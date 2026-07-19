"""Guided Pull Laboratory (PV-19B): expose the full component registry, run the compatible subset as
independent model lenses — with exact scenario identity, correct observable roles, an explicit
component capability/rights matrix, and separated scientific-payload vs build-artifact integrity.

Two modes, kept scrupulously distinct:

* **Common-scenario model lenses** — one bounded espresso scenario is mapped into the *compatible*
  models; each runs independently through its existing authoritative producer. Only
  ``cameron2020.extraction_bdf`` is executed as the common-scenario lens today (via
  ``puckworks.product.simulate_pull``). Every other component gets an honest disposition.
* **Component reference suite** — executable components' native reference cases (registry visibility),
  never presented as predictions of the common shot. Only actually-executed references appear in
  ``executed_reference_results``; the rest are honest coverage placeholders.

This module **duplicates no model equation** (it calls ``simulate_pull`` and the registry), never sums
or averages competing mechanisms, never maps a grinder dial to a universal particle size, never
overlays incompatible concentration reference volumes, and never upgrades an evidence label. It does
**not** run git subprocesses — build provenance is supplied explicitly by the caller.

Schema v3 (distinct from ``PullRun`` v1). Two integrity layers: a wall-clock-free **scientific payload**
hash (stable across build provenance) and a **full artifact** hash (changes with build provenance).

CLI::

    python -m puckworks.product.lab matrix   --format md|json
    python -m puckworks.product.lab compare  --preset pv19_named --format md|json
"""
from __future__ import annotations

import argparse
import dataclasses
import hashlib
import json
import sys

SCHEMA_VERSION = 3
ARTIFACT_SCHEMA_VERSION = 1
_DEFAULT_PRESET = "pv19_named"

# ── finite vocabularies ────────────────────────────────────────────────────────────
DISPOSITIONS = (
    "COMMON_SCENARIO_READY", "COMMON_SCENARIO_WITH_VERIFIED_ADAPTER", "NATIVE_REFERENCE_ONLY",
    "SUPPORTING_STAGE_LENS", "CALIBRATION_OR_CLOSURE", "ADAPTER_REQUIRED", "OUTSIDE_SCENARIO_DOMAIN",
    "RIGHTS_BLOCKED", "NOT_EXECUTABLE", "SKIPPED_OPTIONAL_DEPENDENCY", "FAILED",
)
# runner state for the reference suite (FAILED reserved for an attempted execution that errored)
RUNNER_STATES = (
    "EXECUTED_NATIVE_REFERENCE", "RUNNER_NOT_IMPLEMENTED", "SKIPPED_OPTIONAL_DEPENDENCY",
    "SKIPPED_RUNTIME_BUDGET", "RIGHTS_BLOCKED", "NOT_APPLICABLE", "FAILED",
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

# ── explicit component capability metadata (facts the registry does not encode) ──
# Rights truth is NOT kept here: it lives in the centralized puckworks.rights registry (issue #73), so
# the Lab consumes one authoritative record per component instead of a product-local dictionary.
_OPTIONAL_DEPENDENCY = {"brewer2026.lb_taichi": "taichi"}
_COMMON_SCENARIO_LENSES = {"cameron2020.extraction_bdf": "puckworks.product.simulate_pull"}
# concentration reference basis where known (honest; 'unspecified' otherwise)
_REFERENCE_BASIS = {
    "cameron2020.extraction_bdf": "bed-volume (Cameron c_s0 = 118 / phi_s)",
    "grudeva2025.reduced": "grain-volume incl. internal pores (Grudeva) — not comparable to bed-volume",
    "mo2023_2.coupled_bed": "per bed-depth cell (Mo) — reference basis differs from Cameron",
}

# observable name -> (semantic role, short note). Roles trace the PullRun producer semantics.
_OBSERVABLE_ROLES = {
    "pressure_bar": ("prescribed", "constant input, not predicted"),
    "beverage_mass_g": ("prescribed", "target beverage mass, not a model prediction"),
    "mean_flow_g_s": ("derived", "derived from the prescribed beverage target and modeled shot duration"),
    "shot_duration_s": ("simulated", "modeled shot duration"),
    "extracted_mass_g": ("simulated", ""),
    "extraction_yield_pct": ("simulated", ""),
    "tds_pct": ("simulated", ""),
    "first_drip_s": ("unsupported", "saturated-bed configuration does not model wetting/first drip"),
    "first_modeled_solute_arrival_s":
        ("derived", "numerical diagnostic (first modeled cup solute > 0); NOT physical first drip"),
    "composition": ("reference", "single soluble pool; no per-species composition in this model"),
}
_VALID_ROLES = ("prescribed", "derived", "predicted", "simulated", "fitted", "measured", "unsupported",
                "reference")


# ── typed records (frozen; construction-time validation) ────────────────────────────
@dataclasses.dataclass(frozen=True)
class ScenarioRequest:
    preset_id: str
    overrides: dict = dataclasses.field(default_factory=dict)
    domain_policy: str = "warn"
    requested_lens_ids: tuple = ()
    requested_reference_runner_ids: tuple = ()

    def __post_init__(self):
        import puckworks.product as prod
        if self.preset_id not in prod.available_pull_presets():
            raise ValueError(f"unknown preset_id {self.preset_id!r}")
        allowed = {f.name for f in dataclasses.fields(prod.PullRecipe)}
        bad = set(self.overrides) - allowed
        if bad:
            raise ValueError(f"unknown recipe override field(s): {sorted(bad)}")


@dataclasses.dataclass(frozen=True)
class ScenarioExecution:
    request: ScenarioRequest
    base_recipe: dict
    effective_recipe: dict
    effective_config: dict
    applied_overrides: dict
    pull_run: dict
    domain_findings: tuple
    run_id: str


@dataclasses.dataclass(frozen=True)
class BuildProvenance:
    """Build/artifact identity supplied EXPLICITLY by the caller (never derived via git here)."""
    package_version: str | None = None
    source_commit: str | None = None
    workflow_run_id: str | None = None
    wheel_sha256: str | None = None

    def to_dict(self) -> dict:
        d = {"package_version": self.package_version, "source_commit": self.source_commit,
             "workflow_run_id": self.workflow_run_id, "wheel_sha256": self.wheel_sha256,
             "artifact_schema_version": ARTIFACT_SCHEMA_VERSION}
        return d


def _default_provenance() -> BuildProvenance:
    import puckworks
    return BuildProvenance(package_version=puckworks.__version__)   # version string, not a git call


# ── components ──────────────────────────────────────────────────────────────────────
def _components():
    import puckworks
    return list(puckworks.components())


def _optional_dep_available(dep: str) -> bool:
    import importlib.util
    return importlib.util.find_spec(dep) is not None


# ── scenario execution (exact identity + override provenance) ───────────────────────
def execute_scenario(request: ScenarioRequest) -> ScenarioExecution:
    """Run the authoritative producer for a bounded scenario, preserving the EXACT preset identity and
    the applied overrides. This is the identity-preserving entry point."""
    import puckworks.product as prod
    base_recipe, config = prod.load_pull_preset(request.preset_id)
    base_dict = dataclasses.asdict(base_recipe)
    over = {k: float(v) if isinstance(v, (int, float)) else v for k, v in request.overrides.items()}
    eff_recipe = dataclasses.replace(base_recipe, **over) if over else base_recipe
    applied = {k: {"base": base_dict.get(k), "effective": getattr(eff_recipe, k)} for k in over}
    findings = tuple(_finding_to_dict(f) for f in prod.evaluate_domain(eff_recipe))
    run = prod.pull_run_to_dict(prod.simulate_pull(eff_recipe, config))
    return ScenarioExecution(
        request=request, base_recipe=base_dict, effective_recipe=dataclasses.asdict(eff_recipe),
        effective_config=_config_summary(config), applied_overrides=applied, pull_run=run,
        domain_findings=findings, run_id=run.get("run_id"))


def _config_summary(config) -> dict:
    return {"config_id": getattr(config, "config_id", None),
            "config_version": getattr(config, "config_version", None),
            "domain_policy": getattr(config, "domain_policy", None)}


def _finding_to_dict(f) -> dict:
    if isinstance(f, dict):
        return f
    status = getattr(f, "status", "")
    status = getattr(status, "value", status)
    return {"status": str(status), "field": getattr(f, "field", ""),
            "plain_explanation": getattr(f, "plain_explanation", ""),
            "technical_reason": getattr(f, "technical_reason", ""),
            "supported_range": getattr(f, "supported_range", ""),
            "supplied_value": getattr(f, "supplied_value", None)}


def run_scenario(preset_id: str = _DEFAULT_PRESET, *, dose_g=None, target_beverage_g=None,
                 pressure_bar=None, brew_temperature_c=None) -> dict:
    """DEPRECATED compatibility wrapper. Returns the bare PullRun dict for a bounded scenario.

    A bare PullRun dict cannot carry preset identity, so DO NOT feed it back to build_comparison for a
    non-default preset — use execute_scenario()/build_comparison(execution) instead. Retained for
    external callers that only need the raw run."""
    over = {k: float(v) for k, v in dict(
        dose_g=dose_g, target_beverage_g=target_beverage_g, pressure_bar=pressure_bar,
        brew_temperature_c=brew_temperature_c).items() if v is not None}
    return execute_scenario(ScenarioRequest(preset_id=preset_id, overrides=over)).pull_run


# ── capability / rights matrix ──────────────────────────────────────────────────────
def _lab_spec(comp, executed_common: bool) -> dict:
    name = comp.name
    role = getattr(comp, "execution_role", "")
    stage = getattr(comp, "stage", "")
    kind = getattr(comp, "kind", "")
    has_callable = role in ("runtime", "calibration")     # implemented code exists
    is_runtime_stage = role == "runtime"
    is_calibration = role == "calibration"
    opt_dep = _OPTIONAL_DEPENDENCY.get(name)
    available_in_env = (opt_dep is None) or _optional_dep_available(opt_dep)
    from puckworks import rights
    rights_rec = rights.rights_record(name)
    rights_blocked = rights_rec.is_code_blocked
    is_common_lens = name in _COMMON_SCENARIO_LENSES

    from puckworks.product import lab_runners
    has_native_runner = lab_runners.has_runner(name)
    if rights_blocked:
        disposition = "RIGHTS_BLOCKED"; runner = "RIGHTS_BLOCKED"; adapter = "RIGHTS_BLOCKED"
    elif is_common_lens:
        # the executed common-scenario lens; not a *separate* native reference runner
        disposition = "COMMON_SCENARIO_READY"; runner = "NOT_APPLICABLE"; adapter = "COMMON_SCENARIO_READY"
    elif has_native_runner:
        disposition = "NATIVE_REFERENCE_ONLY"; runner = "EXECUTED_NATIVE_REFERENCE"
        adapter = "ADAPTER_REQUIRED" if stage == "extraction" else "NOT_APPLICABLE"
    elif opt_dep and not available_in_env:
        disposition = "SKIPPED_OPTIONAL_DEPENDENCY"; runner = "SKIPPED_OPTIONAL_DEPENDENCY"; adapter = "NOT_APPLICABLE"
    elif opt_dep:
        disposition = "NATIVE_REFERENCE_ONLY"; runner = "RUNNER_NOT_IMPLEMENTED"; adapter = "NOT_APPLICABLE"
    elif is_calibration:
        disposition = "CALIBRATION_OR_CLOSURE"; runner = "RUNNER_NOT_IMPLEMENTED"; adapter = "NOT_APPLICABLE"
    elif kind in ("reference", "synthesis"):
        disposition = "NATIVE_REFERENCE_ONLY"; runner = "RUNNER_NOT_IMPLEMENTED"; adapter = "NOT_APPLICABLE"
    elif stage == "extraction":
        disposition = "ADAPTER_REQUIRED"; runner = "RUNNER_NOT_IMPLEMENTED"; adapter = "ADAPTER_REQUIRED"
    elif stage in ("bed_dynamics", "flow", "infiltration", "machine"):
        disposition = "SUPPORTING_STAGE_LENS"; runner = "RUNNER_NOT_IMPLEMENTED"; adapter = "ADAPTER_REQUIRED"
    else:
        disposition = "NATIVE_REFERENCE_ONLY"; runner = "RUNNER_NOT_IMPLEMENTED"; adapter = "NOT_APPLICABLE"

    return {
        "component_id": name, "stage": stage, "kind": kind, "execution_role": role,
        "module": comp.module, "provenance_class": comp.provenance_class,
        "evidence_strength": comp.evidence_strength, "n_gates": len(comp.gates),
        "has_callable_code": has_callable, "is_runtime_stage": is_runtime_stage,
        "is_calibration_or_closure": is_calibration,
        "available_in_env": available_in_env, "optional_dependency": opt_dep,
        "rights_state": rights_rec.code_rights_state,
        "code_rights_state": rights_rec.code_rights_state,
        "data_rights_state": rights_rec.data_rights_state,
        "output_redistribution_state": rights_rec.output_redistribution_state,
        "rights_note": rights_rec.rights_note, "rights_decision_issue": rights_rec.decision_issue,
        "native_runner_state": runner, "common_scenario_adapter_state": adapter,
        "concentration_reference_basis": _REFERENCE_BASIS.get(name, "unspecified"),
        "validity_range": comp.valid_range, "disposition": disposition,
    }


def build_matrix(execution: ScenarioExecution) -> list:
    """Every registered component -> exactly one validated Lab capability record (never a substring
    heuristic on the run). Deterministic ordering."""
    executed = {c["component_id"] for c in execution.pull_run.get("coverage", [])
                if c.get("executed")}
    rows = [_lab_spec(c, c.name in executed and c.name in _COMMON_SCENARIO_LENSES)
            for c in _components()]
    seen = {r["component_id"] for r in rows}
    assert len(seen) == len(rows), "duplicate Lab capability record"
    for r in rows:
        assert r["disposition"] in DISPOSITIONS and r["native_runner_state"] in RUNNER_STATES
    rows.sort(key=lambda r: r["component_id"])
    return rows


# ── executed lens (correct observable roles) ────────────────────────────────────────
def _observable_records(run: dict) -> list:
    out = []
    for key, o in sorted(run.get("final_observables", {}).items()):
        if not isinstance(o, dict):
            continue
        role, default_note = _OBSERVABLE_ROLES.get(key, ("derived", ""))
        if o.get("status") == "unavailable":
            role = "unsupported"
        note = o.get("note") or o.get("reason") or default_note
        rec = {"name": key, "value": o.get("value"), "unit": o.get("unit"), "role": role,
               "status": o.get("status", "available"), "note": note}
        if key == "first_modeled_solute_arrival_s":
            rec["is_physical_first_drip"] = False
            rec["semantic_class"] = "diagnostic"
        out.append(rec)
    return out


def _trace_records(run: dict) -> list:
    out = []
    for t in run.get("traces", []):
        series = [{"series_id": s.get("series_id"), "label": s.get("label"), "unit": s.get("unit"),
                   "role": s.get("role"), "values": s.get("values", []), "caveat": s.get("caveat", "")}
                  for s in t.get("series", [])]
        out.append({"trace_id": t.get("trace_id"), "component_id": t.get("component_id"),
                    "observable": t.get("axis_label"), "axis_label": t.get("axis_label"),
                    "axis_unit": t.get("axis_unit"), "axis_values": t.get("axis_values", []),
                    "series": series, "evidence_badge": t.get("evidence_badge"),
                    "evidence_strength": t.get("evidence_strength"),
                    "fidelity_ceiling": t.get("fidelity_ceiling"), "caveat": t.get("caveat", "")})
    return out


def _lens_result(execution: ScenarioExecution) -> dict:
    run = execution.pull_run
    return {
        "component_id": "cameron2020.extraction_bdf",
        "adapter": f"puckworks.product.simulate_pull({execution.request.preset_id})",
        "status": "executed", "disposition": "COMMON_SCENARIO_READY",
        "observables": _observable_records(run),
        "traces": _trace_records(run),
        "domain_findings": list(execution.domain_findings),
        "warnings": run.get("warnings", []),
        "evidence_note": "executed via the existing authoritative producer; no equation is re-implemented",
    }


# ── reference suite (executed vs coverage placeholders, honestly separated) ──────────
def _reference_suite_coverage(matrix: list) -> list:
    out = []
    for row in matrix:
        rs = row["native_runner_state"]
        if rs == "EXECUTED_NATIVE_REFERENCE":
            note = "native reference executed (see executed_reference_results)"
        elif rs == "RIGHTS_BLOCKED":
            note = row["rights_note"] or "rights-blocked; not executed"
        elif rs == "SKIPPED_OPTIONAL_DEPENDENCY":
            note = f"optional dependency '{row['optional_dependency']}' unavailable; a skip is not a pass"
        else:
            note = "Native reference runner not yet implemented; no result was generated."
        out.append({"component_id": row["component_id"], "runner_state": rs, "note": note})
    return out


def _executed_reference_results(execution: ScenarioExecution) -> list:
    """Actually-executed NATIVE reference cases (distinct from the common-scenario lens). The requested
    runners default to the interactive-fast set; per-runner failures are isolated."""
    from puckworks.product import lab_runners
    req = execution.request.requested_reference_runner_ids
    ids = list(req) if req else list(lab_runners.INTERACTIVE_FAST)
    return lab_runners.run_selected(ids)


# ── comparison assembly + integrity ─────────────────────────────────────────────────
def build_comparison(execution: ScenarioExecution, *, provenance: BuildProvenance | None = None) -> dict:
    if isinstance(execution, dict):                       # guard the old identity-losing call shape
        raise TypeError("build_comparison now requires a ScenarioExecution (use execute_scenario); a "
                        "bare PullRun dict cannot carry preset identity")
    prov = provenance or _default_provenance()
    matrix = build_matrix(execution)
    by_disp: dict[str, int] = {}
    for r in matrix:
        by_disp[r["disposition"]] = by_disp.get(r["disposition"], 0) + 1
    lens = _lens_result(execution)
    executed_refs = _executed_reference_results(execution)
    req = execution.request
    scenario = {
        "scenario_id": req.preset_id, "preset_id": req.preset_id,
        "title": f"Guided Pull Laboratory common scenario ({req.preset_id}); one machine/coffee",
        "base_recipe": execution.base_recipe, "effective_recipe": execution.effective_recipe,
        "applied_overrides": execution.applied_overrides,
        "config": execution.effective_config, "domain_policy": req.domain_policy,
        "source": f"puckworks.product.load_pull_preset('{req.preset_id}')"
                  + (" with explicit overrides" if execution.applied_overrides else " (unmodified)"),
        "fixed_assumptions": ["single soluble pool", "saturated bed (no wetting/first drip)",
                              "prescribed constant pressure"],
        "scope": "one bounded scenario, one machine/coffee; grinder dial is non-portable",
        "nonportable_grinder_warning": "a grinder dial is not a universal particle size",
    }
    report = {
        "schema_version": SCHEMA_VERSION,
        "report": "puckworks-guided-pull-laboratory",
        "scenario": scenario,
        "counts": {"components": len(matrix), "executed_common_scenario_lenses": 1,
                   "executed_native_references": sum(1 for r in executed_refs
                                                      if r.get("status") == "executed"),
                   "failed_native_references": sum(1 for r in executed_refs
                                                   if r.get("status") == "FAILED"),
                   "dispositions": dict(sorted(by_disp.items()))},
        "executed_lenses": [lens],
        "excluded_or_dispositioned": [
            {"component_id": r["component_id"], "disposition": r["disposition"],
             "rights_state": r["rights_state"],
             "reason": r["rights_note"] or r["native_runner_state"]}
            for r in matrix if r["disposition"] != "COMMON_SCENARIO_READY"],
        "component_matrix": matrix,
        "executed_reference_results": executed_refs,
        "reference_suite_coverage": _reference_suite_coverage(matrix),
        "what_this_does_not_prove": WHAT_THIS_DOES_NOT_PROVE,
        "fidelity_ceiling": "One bounded scenario on one machine/coffee; one executed extraction lens; "
                            "the rest are independent lenses / native references. Not a validated "
                            "multi-model simulation, not a digital twin, not a best recipe.",
        "provenance": prov.to_dict(),
    }
    # two integrity layers computed over hash-field-free representations
    sci = _scientific_payload(report)
    report.setdefault("integrity", {})["scientific_payload_sha256"] = _sha256_canonical(sci)
    art = _artifact_payload(report)
    report["integrity"]["artifact_sha256"] = _sha256_canonical(art)
    return report


def _scientific_payload(report: dict) -> dict:
    """The science, free of build provenance and integrity fields (stable across builds)."""
    r = json.loads(json.dumps(report))
    r.pop("provenance", None)
    r.pop("integrity", None)
    return r


def _artifact_payload(report: dict) -> dict:
    """The full artifact (incl. provenance + scientific hash) minus its own artifact hash."""
    r = json.loads(json.dumps(report))
    r.get("integrity", {}).pop("artifact_sha256", None)
    return r


def _canonical(obj: dict) -> str:
    return json.dumps(obj, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def _sha256_canonical(obj: dict) -> str:
    return hashlib.sha256(_canonical(obj).encode("utf-8")).hexdigest()


# public integrity API
def scientific_payload(report: dict) -> dict:
    return _scientific_payload(report)


def scientific_json(report: dict) -> str:
    return _canonical(_scientific_payload(report))


def scientific_sha256(report: dict) -> str:
    return report.get("integrity", {}).get("scientific_payload_sha256") or _sha256_canonical(
        _scientific_payload(report))


def artifact_json(report: dict) -> str:
    """The FULL downloadable artifact JSON (carries build provenance + both integrity hashes)."""
    return _canonical(report)


def artifact_sha256(report: dict) -> str:
    return report.get("integrity", {}).get("artifact_sha256") or _sha256_canonical(
        _artifact_payload(report))


# back-compat: the batch/UI download the FULL artifact (not a provenance-stripped payload)
def canonical_json(report: dict) -> str:
    return artifact_json(report)


# ── shared plotting-data layer (used by Streamlit + batch; no science recalculated here) ──
def render_data(report: dict) -> list:
    """Return plot-ready panels straight from the artifact's trace data (units + roles preserved)."""
    panels = []
    for lens in report["executed_lenses"]:
        for t in lens["traces"]:
            series = [s for s in t["series"] if s.get("values")]
            if not series:
                continue
            panels.append({
                "panel_id": t["trace_id"], "component_id": t["component_id"],
                "title": f"{t['component_id']}: {t['observable']}",
                "x_label": f"{t['axis_label']} ({t['axis_unit']})", "x": t["axis_values"],
                "series": [{"label": s["label"] or s["series_id"], "unit": s["unit"],
                            "role": s["role"], "y": s["values"]} for s in series],
                "evidence_badge": t["evidence_badge"], "fidelity_ceiling": t["fidelity_ceiling"],
            })
    return panels


def render_markdown(report: dict) -> str:
    c = report["counts"]; sc = report["scenario"]
    lines = [
        "# Guided Pull Laboratory — model-lens comparison", "",
        "_Independent model lenses over one bounded scenario, plus a component reference suite. "
        "**Not** a validated digital twin; competing mechanisms are never summed or averaged._", "",
        f"- scenario: **{sc['scenario_id']}** (preset `{sc['preset_id']}`, "
        f"{'overridden' if sc['applied_overrides'] else 'unmodified'})",
        f"- registered components: **{c['components']}** · executed common-scenario lenses: "
        f"**{c['executed_common_scenario_lenses']}** · executed native references: "
        f"**{c['executed_native_references']}**", "",
        "## Coverage by disposition", "",
    ]
    for k, v in c["dispositions"].items():
        lines.append(f"- `{k}`: {v}")
    lines += ["", "## Executed common-scenario lens", ""]
    for lens in report["executed_lenses"]:
        lines.append(f"### `{lens['component_id']}` — {lens['status']} ({lens['adapter']})")
        lines.append("")
        lines.append("| observable | value | unit | role | note |")
        lines.append("|---|---|---|---|---|")
        for o in lens["observables"]:
            lines.append(f"| {o['name']} | {o['value']} | {o['unit'] or ''} | {o['role']} | "
                         f"{(o['note'] or '')[:60]} |")
        lines.append("")
    lines += ["## Excluded / dispositioned components (honest, not hidden)", ""]
    for e in report["excluded_or_dispositioned"]:
        lines.append(f"- `{e['component_id']}` — **{e['disposition']}** "
                     f"({e['rights_state']}): {e['reason']}")
    lines += ["", "## Executed native reference results", ""]
    if report["executed_reference_results"]:
        for r in report["executed_reference_results"]:
            lines.append(f"- `{r['component_id']}` — {r['status']} ({r['label']})")
    else:
        lines.append("_None executed._")
    lines += ["", "## Reference-runner coverage", ""]
    for r in report["reference_suite_coverage"]:
        lines.append(f"- `{r['component_id']}` — {r['runner_state']}: {r['note']}")
    lines += ["", "## What this does not prove", ""]
    lines += [f"- {s}" for s in report["what_this_does_not_prove"]]
    lines += ["", f"**Fidelity ceiling.** {report['fidelity_ceiling']}",
              "", "## Provenance / integrity", "",
              f"- package_version: `{report['provenance'].get('package_version')}`",
              f"- source_commit: `{report['provenance'].get('source_commit')}`",
              f"- workflow_run_id: `{report['provenance'].get('workflow_run_id')}`",
              f"- wheel_sha256: `{report['provenance'].get('wheel_sha256')}`",
              f"- scientific_payload_sha256: `{report['integrity']['scientific_payload_sha256']}`",
              f"- artifact_sha256: `{report['integrity']['artifact_sha256']}`", ""]
    return "\n".join(lines)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="puckworks.product.lab", description=__doc__)
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name in ("matrix", "compare"):
        s = sub.add_parser(name)
        s.add_argument("--preset", default=_DEFAULT_PRESET)
        s.add_argument("--format", choices=["md", "json"], default="md")
        s.add_argument("--out", default=None)
    args = ap.parse_args(argv)
    execution = execute_scenario(ScenarioRequest(preset_id=args.preset))
    if args.cmd == "matrix":
        matrix = build_matrix(execution)
        text = (json.dumps(matrix, indent=2, sort_keys=True) + "\n" if args.format == "json"
                else "\n".join(f"{r['component_id']:34} {r['disposition']:28} "
                               f"{r['native_runner_state']:26} {r['rights_state']}"
                               for r in matrix) + "\n")
    else:
        report = build_comparison(execution)
        text = artifact_json(report) if args.format == "json" else render_markdown(report)
    if args.out:
        from pathlib import Path
        Path(args.out).write_text(text, encoding="utf-8")
        print(f"wrote {args.out}")
    else:
        sys.stdout.write(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
