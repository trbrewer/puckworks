"""Reproducible, non-interactive Guided Pull Laboratory batch runner (#43 / #70).

Reads BOUNDED inputs from environment variables (never shell-interpolated), runs the existing
authoritative producer via `puckworks.product.lab.execute_scenario`, and writes the FULL
provenance-bearing artifact JSON + Markdown, at least one SCIENTIFIC trace figure, an optional coverage
diagnostic, and a hash manifest. Build provenance (GITHUB_SHA / GITHUB_RUN_ID / wheel SHA) is supplied
explicitly. No network, no secrets, no scientific literals.

Env inputs (validated + bounded here; out-of-range is REJECTED, never clamped):

    LAB_PRESET  LAB_DOSE_G  LAB_TARGET_BEVERAGE_G  LAB_PRESSURE_BAR  LAB_TEMPERATURE_C
    LAB_OUT_DIR  GITHUB_SHA  GITHUB_RUN_ID  LAB_WHEEL_SHA256
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path

from puckworks.product import lab

_BOUNDS = {
    "LAB_DOSE_G": ("dose_g", 5.0, 30.0),
    "LAB_TARGET_BEVERAGE_G": ("target_beverage_g", 10.0, 80.0),
    "LAB_PRESSURE_BAR": ("pressure_bar", 1.0, 12.0),
    "LAB_TEMPERATURE_C": ("brew_temperature_c", 80.0, 98.0),
}


def _bounded(env: dict) -> dict:
    over = {}
    for var, (field, lo, hi) in _BOUNDS.items():
        raw = env.get(var)
        if raw in (None, ""):
            continue
        try:
            val = float(raw)
        except ValueError as exc:
            raise SystemExit(f"{var}={raw!r} is not a number") from exc
        if not (lo <= val <= hi):
            raise SystemExit(f"{var}={val} out of bounds [{lo}, {hi}]")
        over[field] = val
    return over


def _provenance(env: dict) -> lab.BuildProvenance:
    import puckworks
    return lab.BuildProvenance(
        package_version=puckworks.__version__,
        source_commit=env.get("GITHUB_SHA") or None,
        workflow_run_id=env.get("GITHUB_RUN_ID") or None,
        wheel_sha256=env.get("LAB_WHEEL_SHA256") or None)


def _panel_figure(path: Path, panel: dict) -> None:
    """Render ONE unit-safe panel (a single y-axis carries exactly one unit). The unit-safety is asserted
    again here so a mixed-unit panel can never be drawn."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    lab.assert_unit_safe(panel)
    fig, ax = plt.subplots(figsize=(8, 4.5))
    x = panel["x"]
    for s in panel["series"]:
        style = "--" if s["role"] == "prescribed_input" else "-"
        ax.plot(x, s["y"], style, label=f"{s['label']} [{s['role']}]")
    ax.set_xlabel(panel["x_label"])
    ax.set_ylabel(panel["y_label"])                     # one unit on the axis, always labelled
    ax.set_title(panel["title"])
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(path, dpi=110)
    plt.close(fig)


def _panel_csv(path: Path, panel: dict) -> None:
    """Write the panel's raw x + per-series y as CSV — the text-alternative to the figure (accessibility)
    and a reproducible data table. Columns carry units + roles; no science is recomputed."""
    import csv
    header = [panel["x_label"]] + [f"{s['label']} [{s['role']}, {s['unit']}]" for s in panel["series"]]
    rows = zip(panel["x"], *[s["y"] for s in panel["series"]])
    with open(path, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(header)
        w.writerows(rows)


def _coverage_figure(path: Path, report: dict) -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    disp = report["capability_snapshot"]["dispositions"]
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.barh(list(disp.keys()), list(disp.values()), color="#0e7490")
    ax.set_xlabel("components")
    ax.set_title("Guided Pull Laboratory — coverage by disposition (diagnostic)")
    fig.tight_layout()
    fig.savefig(path, dpi=110)
    plt.close(fig)


def _request_from_env(env: dict, preset: str, over: dict) -> "lab.ScenarioRequest":
    """Build the ScenarioRequest from validated env inputs (all parsed in Python; never shell-interpolated)."""
    kw = {"preset_id": preset, "overrides": over,
          "domain_policy": (env.get("LAB_DOMAIN_POLICY") or "warn")}
    lens_policy = env.get("LAB_LENS_SELECTION_POLICY")
    if lens_policy:
        kw["lens_selection_policy"] = lens_policy
        ids = [x for x in (env.get("LAB_LENS_IDS") or "").split(",") if x]
        if ids:
            kw["requested_lens_ids"] = tuple(ids)
    ref_policy = env.get("LAB_REFERENCE_SELECTION_POLICY")
    if ref_policy:
        kw["reference_selection_policy"] = ref_policy
        ids = [x for x in (env.get("LAB_REFERENCE_IDS") or "").split(",") if x]
        if ids:
            kw["requested_reference_runner_ids"] = tuple(ids)
    return lab.ScenarioRequest(**kw)


def run(env: dict | None = None) -> dict:
    """Atomic: build every output in a STAGING dir, verify the artifact, then rename staging -> final. On
    failure no partially valid final directory is left; a failure summary is written outside it."""
    import shutil
    env = dict(os.environ if env is None else env)
    preset = env.get("LAB_PRESET") or "pv19_named"
    final_dir = Path(env.get("LAB_OUT_DIR") or "out/lab")
    over = _bounded(env)
    execution = lab.execute_scenario(_request_from_env(env, preset, over))
    report = lab.build_comparison(execution, provenance=_provenance(env))

    final_dir.parent.mkdir(parents=True, exist_ok=True)
    out_dir = final_dir.parent / (final_dir.name + ".staging")
    if out_dir.exists():
        shutil.rmtree(out_dir)
    out_dir.mkdir(parents=True)
    files = {}
    (out_dir / "guided_pull_lab.json").write_text(lab.artifact_json(report), encoding="utf-8")
    (out_dir / "guided_pull_lab.md").write_text(lab.render_markdown(report), encoding="utf-8")
    files["guided_pull_lab.json"] = None
    files["guided_pull_lab.md"] = None

    # REQUIRED: at least one unit-safe scientific panel (figure + CSV). No plottable panel -> the job
    # fails (never silently skipped). Every panel is single-unit by construction (lab.render_data).
    panels = lab.render_data(report)
    if not panels:
        raise RuntimeError("no scientific trace panels available to plot")
    panel_inventory = []
    for i, panel in enumerate(panels):
        png = f"guided_pull_lab_panel_{panel['panel_id'].replace('::', '__')}.png"
        csvf = png[:-4] + ".csv"
        _panel_figure(out_dir / png, panel)
        _panel_csv(out_dir / csvf, panel)
        files[png] = None
        files[csvf] = None
        panel_inventory.append({"panel_id": panel["panel_id"], "unit": panel["unit"],
                                "component_id": panel["component_id"], "figure": png, "csv": csvf,
                                "n_series": len(panel["series"])})
    # back-compat required-figure name: the first unit-safe panel (a single, single-unit y-axis)
    _panel_figure(out_dir / "guided_pull_lab_trace.png", panels[0])
    files["guided_pull_lab_trace.png"] = None

    # OPTIONAL diagnostic figure (may be marked skipped without failing the required outputs)
    optional = {"guided_pull_lab_coverage.png": {"required": False}}
    try:
        _coverage_figure(out_dir / "guided_pull_lab_coverage.png", report)
        files["guided_pull_lab_coverage.png"] = None
        optional["guided_pull_lab_coverage.png"]["generated"] = True
    except Exception as exc:                              # pragma: no cover - diagnostic only
        optional["guided_pull_lab_coverage.png"]["generated"] = False
        optional["guided_pull_lab_coverage.png"]["reason"] = str(exc)

    # verify the written artifact (schema + integrity) BEFORE publishing the final directory
    written = json.loads((out_dir / "guided_pull_lab.json").read_text(encoding="utf-8"))
    verification = lab.verify_artifact(written)
    req = report["request"]
    manifest = {
        "schema_version": lab.ARTIFACT_SCHEMA_VERSION,
        "source_commit": report["provenance"].get("source_commit"),
        "workflow_run_id": report["provenance"].get("workflow_run_id"),
        "wheel_sha256": report["provenance"].get("wheel_sha256"),
        "package_version": report["provenance"].get("package_version"),
        "requested_preset": preset,
        "requested_overrides": over,
        "domain_policy": req["domain_policy"],
        "lens_selection_policy": req.get("lens_selection_policy"),
        "requested_lens_ids": req.get("requested_lens_ids", []),
        "reference_selection_policy": req["reference_selection_policy"],
        "requested_reference_runner_ids": req.get("requested_reference_runner_ids", []),
        "scientific_payload_sha256": report["integrity"]["scientific_payload_sha256"],
        "capability_snapshot_sha256": report["integrity"]["capability_snapshot_sha256"],
        "artifact_sha256": report["integrity"]["artifact_sha256"],
        "replay_verification": {"schema_ok": verification["schema"]["ok"],
                                "integrity_ok": verification["integrity"]["ok"]},
        "panel_inventory": panel_inventory,
        "optional_outputs": optional,
        "files": {},
    }
    for name in files:
        p = out_dir / name
        manifest["files"][name] = {"bytes": p.stat().st_size,
                                   "sha256": hashlib.sha256(p.read_bytes()).hexdigest()}
    (out_dir / "artifact_manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    if not (verification["schema"]["ok"] and verification["integrity"]["ok"]):
        # never publish a partially valid final directory; record the failure OUTSIDE it
        (final_dir.parent / (final_dir.name + ".FAILED.json")).write_text(
            json.dumps(verification, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        raise RuntimeError("artifact verification failed; final output not published")
    # atomic publish: replace the final directory with the fully-built, verified staging directory
    if final_dir.exists():
        shutil.rmtree(final_dir)
    os.replace(out_dir, final_dir)
    return report


def main() -> int:
    report = run()
    print(json.dumps({"components": report["counts"]["components"],
                      "executed_lenses": report["counts"]["executed_common_scenario_lenses"],
                      "scenario_id": report["scenario"]["scenario_id"],
                      "scientific_payload_sha256": report["integrity"]["scientific_payload_sha256"]},
                     sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
