"""Reproducible, non-interactive Guided Pull Laboratory batch runner (#43 / #70).

Reads a small set of BOUNDED inputs from environment variables (never shell-interpolated), runs the
existing authoritative producer via ``puckworks.product.lab.run_scenario``, and writes the deterministic
comparison JSON + Markdown and a lightweight figure. No network, no secrets, no scientific literals.

Environment inputs (all optional; validated + bounded here):

    LAB_PRESET             preset id (default pv19_named)
    LAB_DOSE_G             5..30
    LAB_TARGET_BEVERAGE_G  10..80
    LAB_PRESSURE_BAR       1..12
    LAB_TEMPERATURE_C      80..98
    LAB_OUT_DIR            output directory (default: out/lab)

Usage::

    LAB_DOSE_G=18 python tools/lab_batch.py
"""
from __future__ import annotations

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
    """Parse + bound the numeric inputs. Rejects (raises) an out-of-range value; never silently clamps."""
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


def run(env: dict | None = None) -> dict:
    env = dict(os.environ if env is None else env)
    preset = env.get("LAB_PRESET") or "pv19_named"
    out_dir = Path(env.get("LAB_OUT_DIR") or "out/lab")
    over = _bounded(env)
    run_dict = lab.run_scenario(preset, **over)
    report = lab.build_comparison(run_dict)

    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "guided_pull_lab.json").write_text(lab.canonical_json(report), encoding="utf-8")
    (out_dir / "guided_pull_lab.md").write_text(lab.render_markdown(report), encoding="utf-8")
    # a lightweight figure (optional; matplotlib is a webapp/viz extra). Skip cleanly if absent.
    try:
        _write_figure(out_dir / "guided_pull_lab.png", report)
    except Exception as exc:                       # pragma: no cover - figure is best-effort
        (out_dir / "figure_skipped.txt").write_text(f"figure skipped: {exc}\n", encoding="utf-8")
    return report


def _write_figure(path: Path, report: dict) -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    disp = report["counts"]["dispositions"]
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.barh(list(disp.keys()), list(disp.values()), color="#0e7490")
    ax.set_xlabel("components")
    ax.set_title("Guided Pull Laboratory — coverage by disposition")
    fig.tight_layout()
    fig.savefig(path, dpi=110)
    plt.close(fig)


def main() -> int:
    report = run()
    print(json.dumps({"components": report["counts"]["components"],
                      "executed_lenses": report["counts"]["executed_common_scenario_lenses"],
                      "dispositions": report["counts"]["dispositions"]}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
