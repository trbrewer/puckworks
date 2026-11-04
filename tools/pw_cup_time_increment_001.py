"""Run the approved fixed-mass comparison, or report its saved CSVs without fitting."""

import argparse
import csv
from datetime import datetime, timezone
from decimal import Decimal
import hashlib
import json
from pathlib import Path
import platform
import resource
import subprocess
import time

import numpy as np
import scipy

from puckworks.analysis import cup_time_increment as model
from puckworks.analysis import grudeva_clock as clock
from tools import pw_cup_time_increment_001_phase0 as phase0


ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "docs/analysis/pw_cup_time_increment_001"
UPSTREAM = "567ad8f3808eb74fbe3e470eaa333161bf2eac1c"
REPOSITORY = "https://github.com/YoanaGrudeva/espresso-model"
PERMISSION = "https://github.com/trbrewer/puckworks/blob/main/docs/permissions/grudeva2025.md"
ATTRIBUTION = dict(author="Dr. Yoana Grudeva", upstream_repository=REPOSITORY,
                   upstream_commit=UPSTREAM, permissions=PERMISSION,
                   rights="PERMISSION_DOCUMENTED; no SPDX licence; not relicensed under MIT",
                   exp13_sha256=phase0.SOURCE_SHA256)
FILES = ("puckworks/analysis/cup_time_increment.py", "tools/pw_cup_time_increment_001.py",
         "tests/test_cup_time_increment.py", "tools/pw_cup_time_increment_001_phase0.py",
         "puckworks/analysis/grudeva_clock.py", "docs/analysis/pw_cup_time_increment_001/PLAN.md")


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def git(*args):
    return subprocess.check_output(["git", *args], cwd=ROOT, text=True).strip()


def write_json(path, data):
    with path.open("x") as stream:
        json.dump(dict(attribution=ATTRIBUTION, **data), stream, indent=2, allow_nan=False)
        stream.write("\n")


def write_csv(path, rows):
    with path.open("x", newline="") as stream:
        for key, value in ATTRIBUTION.items():
            stream.write(f"# {key}: {value}\n")
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        for row in rows:
            writer.writerow({k: "NA" if isinstance(v, (float, np.floating)) and not np.isfinite(v)
                             else v for k, v in row.items()})


def read_csv(path):
    with path.open() as stream:
        rows = list(csv.DictReader(line for line in stream if not line.startswith("#")))
    for row in rows:
        for key, value in row.items():
            if value == "NA":
                row[key] = float("nan")
            else:
                try:
                    row[key] = float(value)
                except ValueError:
                    pass
    return rows


def qualified_inputs(source):
    pins = json.loads((ROOT / "docs/analysis/sci_md_grudeva_clock_001/SOURCE.json").read_text())
    for name in ("exp13.csv", "PlotData.ipynb"):
        path = source if name == "exp13.csv" else source.parent / name
        if digest(path) != pins["files"][name]:
            raise ValueError(f"STOP: {name} SHA-256 mismatch")
    with source.open() as stream:
        masses = phase0.mass_windows(stream)
    endpoints = tuple(float(r["mass_g"]) for r in phase0.endpoint_summary(masses))
    if endpoints != model.ENDPOINTS:
        raise ValueError("frozen Phase 0 endpoint mismatch")
    # First chemistry access in this task: unchanged CLOCK functions, after
    # committed approval corrections and recorded synthetic interpolation QA.
    rows = clock.observations(clock.parse_source(source))
    groups = {shot: [r for r in rows if r["shot"] == shot] for shot in range(1, 14)}
    selected = tuple(shot for shot, group in groups.items()
                     if all(r["mass_g"] == 0 or r["eligible"] for r in group))
    if selected != phase0.PRIMARY_SHOTS:
        raise ValueError(f"PRIMARY_SHOTS mismatch: {selected!r}")
    checks = []
    for shot in selected:
        for mass in model.ENDPOINTS:
            actual = model.prefix_observation(groups[shot], mass)["duration_s"]
            expected = float(phase0.duration_at_mass(masses[shot], Decimal(str(mass))))
            difference = actual - expected
            checks.append(dict(shot=shot, mass_g=mass, duration_s=actual,
                               phase0_duration_s=expected, difference_s=difference))
            if abs(difference) > 1e-10:
                raise ValueError(f"Phase 0 timing mismatch: {checks[-1]!r}")
    return {shot: groups[shot] for shot in selected}, checks


def run(source, out):
    start = time.perf_counter()
    out.mkdir(parents=True, exist_ok=True)
    if git("status", "--porcelain", "--", *FILES):
        raise ValueError("commit approved plan, implementation and tests before chemistry access")
    qa = json.loads((DOC / "QA.json").read_text())
    if not qa["checks"] or not all(c["exit_code"] == 0 for c in qa["checks"]):
        raise ValueError("pre-chemistry synthetic QA unavailable")
    code_hashes = {name: digest(ROOT / name) for name in FILES}
    if qa["pre_chemistry_code_sha256"] != code_hashes:
        raise ValueError("pre-chemistry QA code identity changed")
    clock_original = subprocess.check_output(
        ["git", "show", "e3560148f1fb93a8ff14da5822e33d095d721456:puckworks/analysis/grudeva_clock.py"],
        cwd=ROOT)
    if hashlib.sha256(clock_original).hexdigest() != code_hashes[FILES[4]]:
        raise ValueError("CLOCK implementation changed")
    started = dict(utc=datetime.now(timezone.utc).isoformat(), implementation_commit=git("rev-parse", "HEAD"),
                   code_sha256=code_hashes, pre_chemistry_qa_sha256=digest(DOC / "QA.json"),
                   plan_corrections_commit="f88ae1f2941930598a76f51fafc87dccc57bffe1")
    write_json(out / "RUN_STARTED.json", started)
    try:
        groups, checks = qualified_inputs(source)
        write_csv(out / "timing_reconciliation.csv", checks)
        multiplicities, permutations = model.resampling_indices()
        observations, folds, boot_records, perm_records, summaries = [], [], [], [], []
        for variant, mass, timing, interpolate in model.VARIANTS:
            observed = [dict(variant=variant, shot=shot,
                             **model.prefix_observation(rows, mass, timing, interpolate))
                        for shot, rows in groups.items()]
            observations.extend(observed)
            duration = np.array([r["duration_s"] for r in observed])
            outcome = np.array([r["concentration_tds_pp"] for r in observed])
            point, per_fold = model.point_analysis(duration, outcome)
            folds.extend(dict(variant=variant, shot=phase0.PRIMARY_SHOTS[f["held_index"]], **f)
                         for f in per_fold)
            boots, perms = model.resample_analysis(duration, outcome, multiplicities, permutations)
            for i, record in enumerate(boots):
                counts = ";".join(str(int(w)) for w in multiplicities[i])
                boot_records.append(dict(variant=variant, multiplicities_in_PRIMARY_SHOTS_order=counts,
                                         **record))
            for i, record in enumerate(perms):
                order = ";".join(str(phase0.PRIMARY_SHOTS[j]) for j in permutations[i])
                perm_records.append(dict(variant=variant, duration_source_shots=order, **record))
            summaries.append(dict(variant=variant, mass_g=mass, **point,
                                  **model.uncertainty_summary(point, boots, perms)))
            print(f"Completed {variant}: 2000 grouped bootstrap + 2000 permutation draws", flush=True)
        for filename, rows in (("observations.csv", observations), ("folds.csv", folds),
                               ("bootstrap_draws.csv", boot_records), ("permutation_draws.csv", perm_records),
                               ("summaries.csv", summaries)):
            write_csv(out / filename, rows)
        report(out)
        process = resource.getrusage(resource.RUSAGE_SELF)
        workers = resource.getrusage(resource.RUSAGE_CHILDREN)
        execution = dict(**started, source_sha256=phase0.SOURCE_SHA256,
                         notebook_sha256=clock.NOTEBOOK_SHA, notebook_executed=False,
                         primary_shots=list(groups), frozen_endpoints_g=list(model.ENDPOINTS),
                         timing_checks=len(checks), timing_max_abs_difference_s=max(
                             abs(c["difference_s"]) for c in checks),
                         numpy_seed_sequence=model.SEED, bit_generator="PCG64",
                         bootstrap_spawn_key=[0], permutation_spawn_key=[1],
                         draws_per_variant_per_method=model.DRAWS, variants=len(model.VARIANTS),
                         process_cpu_core_hours=(process.ru_utime + process.ru_stime)/3600,
                         worker_and_child_cpu_core_hours=(workers.ru_utime + workers.ru_stime)/3600,
                         computational_workers=0, blas_threads=1,
                         wall_seconds=time.perf_counter()-start,
                         python=platform.python_version(), numpy=np.__version__, scipy=scipy.__version__,
                         measurement="through report generation; excludes final execution-receipt serialization",
                         output_sha256={p.name: digest(p) for p in sorted(out.iterdir())
                                        if p.suffix in (".csv", ".png") or p.name == "SUMMARY.md"})
        write_json(out / "EXECUTION.json", execution)
    except Exception as exc:
        write_json(out / "FAILURE.json", dict(error_type=type(exc).__name__,
                                            evidence=str(exc).replace(str(source), "[external source]")))
        raise


def interval(row, key):
    return f"[{row[key+'_boot_low']:.3f}, {row[key+'_boot_high']:.3f}]"


def report(out):
    """Render saved artifacts only; never parse originals or refit."""
    summaries = read_csv(out / "summaries.csv")
    obs = read_csv(out / "observations.csv")
    folds = read_csv(out / "folds.csv")
    primary, primary_obs = summaries[0], [r for r in obs if r["variant"] == "primary"]
    primary_folds = [r for r in folds if r["variant"] == "primary"]
    direction, delta_words, beta_words = model.vocabulary(primary)
    lines = ["# PW-CUP-TIME-INCREMENT-001 — fixed-mass prefix TDS", "",
             f"**11 shots; M*=19.8 g. A0 RMSE {primary['rmse_A0_pp']:.3f} pp "
             f"(95% bootstrap {interval(primary, 'rmse_A0_pp')}); A1 {primary['rmse_A1_pp']:.3f} pp "
             f"({interval(primary, 'rmse_A1_pp')}). Δ={primary['delta_pp']:+.3f} pp "
             f"({interval(primary, 'delta_pp')}): {delta_words}.** "
             f"The point direction is an error {direction}. This Δ statement answers the prediction question.", "",
             "| Shot | t(M*) s | C(M*) TDS pp | A0 error pp | A1 error pp |",
             "|---|---:|---:|---:|---:|"]
    for row, fold in zip(primary_obs, primary_folds):
        lines.append(f"| {int(row['shot'])} | {row['duration_s']:.3f} | "
                     f"{row['concentration_tds_pp']:.3f} | {fold['A0_error_pp']:+.3f} | "
                     f"{fold['A1_error_pp']:+.3f} |")
    lines += ["", "Errors are observed minus held-out prediction. Original physical-block IDs; "
              "mass is 19.8 g for every row. [All endpoints](observations.csv) · "
              "[fold coefficients, predictions and influence](folds.csv).", "",
              f"**Duration association: {beta_words}.** β={primary['beta']:+.3f} pp per unit ln(t/20 s), "
              f"95% bootstrap {interval(primary, 'beta')}. Implied change over "
              f"{primary['duration_min_s']:.3f}–{primary['duration_max_s']:.3f} s: "
              f"{primary['implied_change_pp']:+.3f} pp {interval(primary, 'implied_change_pp')}. "
              f"**DESCRIPTIVE_ALL (in-sample):** Student-t 95% β interval "
              f"[{primary['descriptive_all_beta_t_low']:.3f}, {primary['descriptive_all_beta_t_high']:.3f}], "
              "9 df; it does not determine the reporting vocabulary.", "",
              "| Sensitivity | A0 / A1 RMSE pp | Δ pp [95% bootstrap] | β [95% bootstrap] |",
              "|---|---:|---:|---:|"]
    labels = {"time_u2": "Timing u²", "time_sqrt": "Timing √u",
              "conserving_interpolation": "Conserving interpolation", "secondary_0.5": "9.90 g",
              "secondary_0.75": "14.85 g"}
    for row in summaries[1:]:
        lines.append(f"| {labels[row['variant']]} | {row['rmse_A0_pp']:.3f} / {row['rmse_A1_pp']:.3f} | "
                     f"{row['delta_pp']:+.3f} {interval(row, 'delta_pp')} | "
                     f"{row['beta']:+.3f} {interval(row, 'beta')} |")
    unfit = sum(r['bootstrap_unfit_slope_draws'] for r in summaries)
    lines += ["", "Each sensitivity refits training shots separately; no families are combined. "
              "Secondary endpoints reuse all 11 shots; agreement is not independent confirmation.", "",
              f"**Uncertainty/influence:** 2,000 bootstrap and 2,000 permutation draws per variant; "
              f"{int(unfit)} variant-draws have an unfit slope fold. "
              f"Primary Δ/β intervals use {int(primary['delta_pp_boot_defined'])}/"
              f"{int(primary['beta_boot_defined'])} defined draws. "
              f"Observed primary Δ is at the {primary['permutation_percentile']:.2f}th percentile "
              "of duration-shuffled Δ (descriptive). "
              f"A1 improves {int(primary['shots_A1_better'])}/11 shots; maximum A1 leverage "
              f"{primary['A1_h_ii_max']:.3f}; fold β range "
              f"[{primary['A1_beta_min']:.3f}, {primary['A1_beta_max']:.3f}]; paired squared-error "
              f"difference range [{primary['paired_squared_error_difference_pp2_min']:.3f}, "
              f"{primary['paired_squared_error_difference_pp2_max']:.3f}] pp². "
              "All finite-only interval denominators, failure counts and ranges are in "
              "[summaries.csv](summaries.csv); all requested draws are retained.", "",
              "Retrospective conditional prediction, not a fixed-grind experiment: EK43 2.85–3.1 "
              "varies and is not recorded per shot; the thesis excludes channelled/clogged shots. "
              "A resolved β alone does not establish improved held-out prediction; neither result "
              "identifies a causal mechanism. An interval including zero establishes neither negligible "
              "sensitivity nor equivalence. EY at fixed mass/nominal dose rescales TDS, adding no "
              "separate evidence. Intervals omit shared calibration and other unmodelled errors; "
              "no gates, pass/fail grades, or independent-campaign claim.", "",
              "[Plan](PLAN.md) · [plots](primary.png) · [sensitivity intervals](sensitivities.png) · "
              "[draw distributions](uncertainty.png) · [CPU/execution](EXECUTION.json) · [QA](QA.json). "
              "EWP untouched; PR remains draft/unmerged.", "",
              f"Attribution: **Dr. Yoana Grudeva**, [espresso-model@{UPSTREAM}]({REPOSITORY}/tree/{UPSTREAM}); "
              "[permission](../../permissions/grudeva2025.md): **PERMISSION_DOCUMENTED; no SPDX licence; "
              "not relicensed under MIT**. No Pocket Science-derived data."]
    (out / "SUMMARY.md").write_text("\n".join(lines) + "\n")
    make_plots(out, summaries, primary_obs, primary_folds)


def make_plots(out, summaries, observations, folds):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    footer = (f"Dr. Yoana Grudeva | {REPOSITORY}\ncommit {UPSTREAM}\n"
              "PERMISSION_DOCUMENTED; no SPDX licence; not relicensed under MIT\n"
              "docs/permissions/grudeva2025.md (linked in image metadata)")
    metadata = {**{k: str(v) for k, v in ATTRIBUTION.items()}, "Description": footer}

    def save(fig, name):
        fig.text(0.02, 0.015, footer, fontsize=7, va="bottom")
        fig.tight_layout(rect=(0, 0.15, 1, 0.97))
        fig.savefig(out / name, dpi=160, metadata=metadata)
        plt.close(fig)

    p = summaries[0]
    fig, axes = plt.subplots(1, 2, figsize=(11, 5))
    times = np.array([r['duration_s'] for r in observations])
    values = [r['concentration_tds_pp'] for r in observations]
    axes[0].scatter(times, values, color="#1f5d75")
    for row in observations:
        axes[0].annotate(str(int(row['shot'])), (row['duration_s'], row['concentration_tds_pp']),
                         xytext=(4, 4), textcoords='offset points', fontsize=8)
    grid = np.linspace(min(times), max(times), 100)
    axes[0].plot(grid, p['A1_all_alpha'] + p['beta']*np.log(grid/20), label='DESCRIPTIVE_ALL A1')
    axes[0].axhline(p['A0_all_alpha'], color='gray', linestyle='--', label='DESCRIPTIVE_ALL A0')
    axes[0].set(xlabel='Activation-clock duration (s)', ylabel='Collected-prefix TDS (pp)',
                title='19.8 g prefix: observations and in-sample fits')
    axes[0].legend(fontsize=8)
    x = np.arange(len(folds))
    axes[1].bar(x-0.18, [r['A0_error_pp'] for r in folds], 0.36, label='A0 LOSO')
    axes[1].bar(x+0.18, [r['A1_error_pp'] for r in folds], 0.36, label='A1 LOSO')
    axes[1].axhline(0, color='black', linewidth=0.6)
    axes[1].set(xticks=x, xticklabels=[int(r['shot']) for r in folds], xlabel='Physical shot',
                ylabel='Observed minus predicted TDS (pp)', title='Held-out errors (11 physical-shot folds)')
    axes[1].legend(fontsize=8)
    save(fig, 'primary.png')

    fig, axes = plt.subplots(1, 2, figsize=(11, 5))
    labels = ['Primary', 'Timing u²', 'Timing √u', 'Conserving interpolation', '9.90 g', '14.85 g']
    for ax, key, title in zip(axes, ('delta_pp', 'beta'), ('Held-out Δ (pp)', 'Duration slope β (pp)')):
        for i, r in enumerate(summaries):
            # Draw interval separately: percentile CIs need not contain the point estimate.
            ax.plot([r[key+'_boot_low'], r[key+'_boot_high']], [i, i], color='#1f5d75', linewidth=2)
            ax.scatter(r[key], i, color='#ad4b31', s=25, zorder=3)
        ax.axvline(0, color='gray', linestyle='--')
        ax.set(yticks=np.arange(6), yticklabels=labels, xlabel=title,
               title='Point estimate and bootstrap 95% interval')
        ax.invert_yaxis()
    save(fig, 'sensitivities.png')

    fig, axes = plt.subplots(1, 2, figsize=(11, 5))
    for ax, filename, title in zip(axes, ('bootstrap_draws.csv', 'permutation_draws.csv'),
                                   ('Whole-shot bootstrap Δ', 'Duration-permuted LOSO Δ')):
        values = [r['delta_pp'] for r in read_csv(out / filename) if r['variant'] == 'primary']
        defined = np.array(values)[np.isfinite(values)]
        ax.hist(defined, bins=40, color='#658c9b', edgecolor='white')
        ax.axvline(p['delta_pp'], color='#ad4b31', label='Observed Δ')
        ax.axvline(0, color='gray', linestyle='--')
        ax.set(xlabel='RMSE(A1) − RMSE(A0) (pp)', ylabel='Draw count',
               title=f'{title}\n{len(defined)}/2000 defined')
        ax.legend(fontsize=8)
    save(fig, 'uncertainty.png')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=('run', 'report'))
    parser.add_argument('--source', type=Path)
    parser.add_argument('--output', type=Path, default=DOC)
    args = parser.parse_args()
    if args.command == 'run':
        if args.source is None:
            parser.error('--source is required for run')
        run(args.source, args.output)
    else:
        report(args.output)


if __name__ == '__main__':
    main()
