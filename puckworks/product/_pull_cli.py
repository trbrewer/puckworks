"""CLI for the Guided Espresso Pull — ``puckworks-pull`` (issue #48).

CPU-only, no network, no private data. Same validation as the Python API. Warnings go to stderr and
into the exported reports; exit is nonzero for REJECTED input or a failed primary stage, and zero for
a completed warning-mode extrapolation (with a conspicuous warning summary).
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from ._pull import (
    PullConfig,
    PullDomainError,
    PullEvent,
    PullRecipe,
    available_pull_presets,
    load_pull_preset,
    pull_run_to_json,
    pull_run_to_markdown,
    pull_run_summary,
    simulate_pull,
)


def _progress(event: PullEvent, payload: dict) -> None:
    if event is PullEvent.STAGE_STARTED:
        print(f"  … {payload.get('stage')}", file=sys.stderr)
    elif event is PullEvent.STAGE_WARNING:
        print(f"  ⚠ {payload.get('stage')}: {payload.get('field')} out of evidence range",
              file=sys.stderr)


def _apply_overrides(recipe: PullRecipe, config: PullConfig, args) -> PullRecipe:
    changes = {}
    for field, val in (("dose_g", args.dose_g), ("target_beverage_g", args.beverage_g),
                       ("brew_temperature_c", args.temperature_c), ("pressure_bar", args.pressure_bar),
                       ("grind_setting", args.grind_setting), ("coffee_profile", args.coffee_profile),
                       ("bean_label", args.bean_label), ("grinder_model", args.grinder_model)):
        if val is not None:
            if config.editable_fields and field not in config.editable_fields and field != "grinder_model":
                raise PullDomainError(f"{field} is not editable in preset {config.config_id!r}")
            changes[field] = val
    from dataclasses import replace
    return replace(recipe, **changes) if changes else recipe


def _cmd_presets(_args) -> int:
    for pid in available_pull_presets():
        recipe, config = load_pull_preset(pid)
        editable = ", ".join(config.editable_fields) or "(fixed reference)"
        print(f"{pid}: policy={config.domain_policy}; editable: {editable}")
    return 0


def _cmd_run(args) -> int:
    recipe, config = load_pull_preset(args.preset)
    recipe = _apply_overrides(recipe, config, args)
    if args.domain_policy:
        from dataclasses import replace
        config = replace(config, domain_policy=args.domain_policy)
    run = simulate_pull(recipe, config, progress=_progress)

    if args.format == "json":
        out = pull_run_to_json(run)
    elif args.format == "markdown":
        out = pull_run_to_markdown(run)
    else:
        out = pull_run_summary(run) + "\n"

    if args.out:
        base = Path(args.out)
        base.parent.mkdir(parents=True, exist_ok=True)
        base.with_suffix(".json").write_text(pull_run_to_json(run), encoding="utf-8")
        base.with_suffix(".md").write_text(pull_run_to_markdown(run), encoding="utf-8")
        print(f"wrote {base.with_suffix('.json')} and {base.with_suffix('.md')}", file=sys.stderr)
    print(out, end="" if out.endswith("\n") else "\n")

    if run.warnings:
        print(f"⚠ {len(run.warnings)} domain warning(s) — result is an EXTRAPOLATION beyond the "
              "validated range:", file=sys.stderr)
        for w in run.warnings:
            print(f"    - {w}", file=sys.stderr)
    if run.completion_state == "failed":
        return 1
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="puckworks-pull", description=__doc__)
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("presets", help="list available presets and their editable fields")

    r = sub.add_parser("run", help="run a guided espresso pull")
    r.add_argument("--preset", default="guided_v1", choices=list(available_pull_presets()))
    r.add_argument("--dose-g", type=float, dest="dose_g")
    r.add_argument("--beverage-g", type=float, dest="beverage_g")
    r.add_argument("--temperature-c", type=float, dest="temperature_c")
    r.add_argument("--pressure-bar", type=float, dest="pressure_bar")
    r.add_argument("--grinder-model", dest="grinder_model")
    r.add_argument("--grind-setting", type=float, dest="grind_setting")
    r.add_argument("--coffee-profile", dest="coffee_profile")
    r.add_argument("--bean-label", dest="bean_label")
    r.add_argument("--domain-policy", choices=["warn", "strict"], default=None)
    r.add_argument("--format", choices=["summary", "json", "markdown"], default="summary")
    r.add_argument("--out", default=None, help="write <out>.json and <out>.md")

    args = ap.parse_args(argv)
    try:
        if args.cmd == "presets":
            return _cmd_presets(args)
        return _cmd_run(args)
    except PullDomainError as exc:
        print(f"REJECTED: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
