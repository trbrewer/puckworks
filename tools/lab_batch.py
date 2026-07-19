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


def _sci_figure(path: Path, report: dict) -> None:
    """Render at least one SCIENTIFIC trace panel. Raises if no plottable trace exists (the caller
    fails the job — this is a required figure, never silently skipped)."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    panels = lab.render_data(report)
    if not panels:
        raise RuntimeError("no scientific trace panels available to plot")
    panel = panels[0]
    fig, ax = plt.subplots(figsize=(8, 4.5))
    x = panel["x"]
    for s in panel["series"]:
        style = "--" if s["role"] == "prescribed_input" else "-"
        ax.plot(x, s["y"], style, label=f"{s['label']} [{s['role']}]")
    ax.set_xlabel(panel["x_label"])
    ax.set_title(panel["title"])
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(path, dpi=110)
    plt.close(fig)


def _coverage_figure(path: Path, report: dict) -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    disp = report["counts"]["dispositions"]
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.barh(list(disp.keys()), list(disp.values()), color="#0e7490")
    ax.set_xlabel("components")
    ax.set_title("Guided Pull Laboratory — coverage by disposition (diagnostic)")
    fig.tight_layout()
    fig.savefig(path, dpi=110)
    plt.close(fig)


def run(env: dict | None = None) -> dict:
    env = dict(os.environ if env is None else env)
    preset = env.get("LAB_PRESET") or "pv19_named"
    out_dir = Path(env.get("LAB_OUT_DIR") or "out/lab")
    over = _bounded(env)
    execution = lab.execute_scenario(lab.ScenarioRequest(preset_id=preset, overrides=over))
    report = lab.build_comparison(execution, provenance=_provenance(env))

    out_dir.mkdir(parents=True, exist_ok=True)
    files = {}
    (out_dir / "guided_pull_lab.json").write_text(lab.artifact_json(report), encoding="utf-8")
    (out_dir / "guided_pull_lab.md").write_text(lab.render_markdown(report), encoding="utf-8")
    files["guided_pull_lab.json"] = None
    files["guided_pull_lab.md"] = None
    # REQUIRED scientific figure (failure raises -> the job fails; never silently skipped)
    _sci_figure(out_dir / "guided_pull_lab_trace.png", report)
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

    manifest = {
        "schema_version": lab.ARTIFACT_SCHEMA_VERSION,
        "source_commit": report["provenance"].get("source_commit"),
        "workflow_run_id": report["provenance"].get("workflow_run_id"),
        "wheel_sha256": report["provenance"].get("wheel_sha256"),
        "package_version": report["provenance"].get("package_version"),
        "requested_preset": preset,
        "requested_overrides": over,
        "scientific_payload_sha256": report["integrity"]["scientific_payload_sha256"],
        "artifact_sha256": report["integrity"]["artifact_sha256"],
        "optional_outputs": optional,
        "files": {},
    }
    for name in files:
        p = out_dir / name
        manifest["files"][name] = {"bytes": p.stat().st_size,
                                   "sha256": hashlib.sha256(p.read_bytes()).hexdigest()}
    (out_dir / "artifact_manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
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
