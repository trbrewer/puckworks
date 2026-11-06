# Reproduction

Use Python >=3.10 with the repository development dependencies, Numba and
Matplotlib. Source originals, retained native configurations, historical fit JSON,
and all large new traces/trials remain outside Git. EWP is only read.

```bash
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 NUMBA_NUM_THREADS=1
export PYTHONPATH=.
PY=/path/to/environment/bin/python
WORK=/path/to/new/external/task-artifacts
inputs=(
  --ewp /path/to/read-only/ewp-form-a-reference
  --native /path/to/FORM_A/campaign
  --raw /path/to/waszkiewicz/upstream
  --screen /path/to/WETTING_SCREEN_001/artifacts
  --joint /path/to/JOINT_CLOCK_001/artifacts
  --lc /path/to/LC_JOINT_TRANSFER_001/artifacts
  --wasz /path/to/checkout-at-c4b4a07e110a3ede5013fd876a02a58ee6456eab
  --replay /path/to/checkout-at-ec82d1f019da3a5fcd9ff8748c29926c763d7bcc
  --work "$WORK"
)
"$PY" -m pytest -q tests/test_joint_mass_fade_001.py tests/test_joint_clock_001.py tests/test_wetting_screen_001.py
/usr/bin/time -v -o "$WORK/reference-time.txt" "$PY" -m puckworks.analysis.joint_mass_fade_001_run reference "${inputs[@]}" --workers 48
/usr/bin/time -v -o "$WORK/control-time.txt" "$PY" -m puckworks.analysis.joint_mass_fade_001_run control "${inputs[@]}" --workers 48
/usr/bin/time -v -o "$WORK/fade-time.txt" "$PY" -m puckworks.analysis.joint_mass_fade_001_run fade "${inputs[@]}" --workers 48
/usr/bin/time -v -o "$WORK/evaluate-time.txt" "$PY" -m puckworks.analysis.joint_mass_fade_001_evaluate "${inputs[@]}" --workers 32
/usr/bin/time -v -o "$WORK/report-time.txt" "$PY" -m puckworks.analysis.joint_mass_fade_001_report "${inputs[@]}"
```

Run from this checkout so the local predictor is imported. Git objects for the
pinned base and LC/#423/#424 heads must be available for provenance verification.
PLAN.md and START_BANK.csv must be committed before `control`; the runner checks
that. The exact pre-fit commit is `5e5e8c6`. No optimization occurs in reference,
evaluate or report. The fixed bank has 24 problems/456 starts, lambda=1 only.
Each control completes before the corresponding refreshed vector becomes a fade
seed; the command sequence completes all controls before all fade fits.

The first four fade start vectors use only the matching selected control and
predeclared products 0,.03,.13,.25. The remaining 15 reuse the exact Step 1 LHS
common vectors; initial products are frozen in START_BANK.csv. STARTS.csv records
realized vectors, all retained start outcomes, best-finite objectives and trial
hashes. The optimizer has no iteration, evaluation or wall-clock cap. Re-running
completed starts reuses them only when the fitting identity matches exactly.
Preserve a failed attempt before any retry; include every attempt's process-tree
CPU in accounting. Per-start CPU is diagnostic, not the all-command total.

The inherited source loader checks raw file hashes, native configurations,
observed onset and fixed scoring masks. SOURCE_FITS.json binds large historical
fits to the pinned compact tables and matching training membership/Mc. Imported
observation/replay modules are bound by IMPORTED_SOURCES.json. Reference replays
12 saved objectives, 12 LC frozen-zero objectives and all 79 original J1 cases at
both steps with rtol=1e-12, atol=0. Selected predictions use recorded pressure
through the original clean end. Missing evidence causes failure, never shorter
support or false censoring. Native cumulative-mass observation and 2-s averaging
reuse #424 unchanged; applying that observer separately to retained liquid and
solute follows #425 and must reconstruct total to rtol=atol=1e-12.

Trajectory intervals use the exact #423/#424 1,000 within-condition brew bank,
SHA256 `d599d80c854fd5a3cf9b9ca5d6fe1c617b222125bd1adcb36ad9edecd96801b6`.
Full-cohort J1 RMSE intervals use its separate inherited 1,000 condition-then-brew
bank, seed 20261103. Per-condition RMSE contrasts use the shared whole-brew bank.
All are conditional on frozen fits/fixed Mc and omit refit uncertainty. Reported
onset differences involving censored predictions subtract computed bounds;
they are not bounds on unknown true-error differences.

Peak rows report native beverage-observer maxima per brew and equal-brew
condition means interpolated at .1 s on common clean support. Exact tied maximum
times, boundary flags, interior local maxima and horizons are retained. When the
global maximum is only at a boundary, `no interior peak within horizon` is used;
a fully flat curve has no unique peak. Analytic M* describes only constant-pressure
liquid flow and must not be read as a beverage peak or a pressure ordering.

Required checks:

```bash
"$PY" -m pytest -q -m 'not slow and not live and not gpu and not external_data'
"$PY" -m ruff check puckworks/ tests/
"$PY" -c 'from puckworks.registry import run_all_gates; run_all_gates()'
git diff --check
```

Hosted required workflows and fresh read-only final review are recorded at
closeout. This run does not write EWP, refit Mc, tune chemistry, add another arm
or start a successor.
