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


def _require_editable(config: PullConfig, field: str) -> None:
    """Enforce the preset's editability policy for one field.
    editable_fields is None -> unrestricted; a tuple (incl. the empty tuple for a FIXED preset)
    -> only the named fields may change. No field (grinder_model, domain_policy, ...) is exempt."""
    if config.editable_fields is not None and field not in config.editable_fields:
        raise PullDomainError(f"{field} is not editable in preset {config.config_id!r}")


def _apply_overrides(recipe: PullRecipe, config: PullConfig, args) -> PullRecipe:
    changes = {}
    for field, val in (("dose_g", args.dose_g), ("target_beverage_g", args.beverage_g),
                       ("brew_temperature_c", args.temperature_c), ("pressure_bar", args.pressure_bar),
                       ("grind_setting", args.grind_setting), ("coffee_profile", args.coffee_profile),
                       ("bean_label", args.bean_label), ("grinder_model", args.grinder_model)):
        if val is not None:
            _require_editable(config, field)
            changes[field] = val
    from dataclasses import replace
    return replace(recipe, **changes) if changes else recipe


def _cmd_presets(_args) -> int:
    for pid in available_pull_presets():
        recipe, config = load_pull_preset(pid)
        editable = ("(unrestricted)" if config.editable_fields is None
                    else ", ".join(config.editable_fields) or "(fixed reference)")
        print(f"{pid}: policy={config.domain_policy}; editable: {editable}")
    return 0


def _cmd_run(args) -> int:
    from ._pull import DomainStatus, render_pull_report

    recipe, config = load_pull_preset(args.preset)
    recipe = _apply_overrides(recipe, config, args)
    if args.domain_policy:
        _require_editable(config, "domain_policy")   # domain_policy obeys the same editability policy
        from dataclasses import replace
        config = replace(config, domain_policy=args.domain_policy)
    run = simulate_pull(recipe, config, progress=_progress)

    if args.format == "json":
        out = pull_run_to_json(run)
    elif args.format == "markdown":
        out = pull_run_to_markdown(run)
    else:
        out = pull_run_summary(run) + "\n"

    # Full visual report (JSON + Markdown + figures) needs a directory and the [viz] extra.
    report_dir = args.report_dir or (args.out if args.figures else None)
    if args.figures or args.report_dir:
        if not report_dir:
            report_dir = "guided-pull-report"
        try:
            art = render_pull_report(run, report_dir, overwrite=True)
        except ModuleNotFoundError as exc:
            print(f"cannot render figures: {exc}", file=sys.stderr)
            return 3
        print(f"wrote report ({len(art.files)} files) to {art.out_dir}", file=sys.stderr)
    elif args.out:
        base = Path(args.out)
        base.parent.mkdir(parents=True, exist_ok=True)
        base.with_suffix(".json").write_text(pull_run_to_json(run), encoding="utf-8")
        base.with_suffix(".md").write_text(pull_run_to_markdown(run), encoding="utf-8")
        print(f"wrote {base.with_suffix('.json')} and {base.with_suffix('.md')}", file=sys.stderr)

    print(out, end="" if out.endswith("\n") else "\n")

    # First drip is unavailable (not modeled) — printed as unavailable, never as 0.
    fd = run.final_observables["first_drip_s"]
    print(f"first drip: {fd.get('status', 'unavailable')} (not modeled: saturated-bed primary model)",
          file=sys.stderr)
    if any(f.status is DomainStatus.NOT_APPLICABLE and f.field == "brew_temperature_c"
           for f in run.domain_findings):
        print("note: brew_temperature_c is recorded-only — it does not affect the v0.3.0 model",
              file=sys.stderr)

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
    r.add_argument("--report-dir", dest="report_dir", default=None,
                   help="render the full visual report (JSON + Markdown + figures) into this directory")
    r.add_argument("--figures", action="store_true",
                   help="also render figures (into --report-dir, else --out, else ./guided-pull-report); "
                        "needs the puckworks[viz] extra")

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
