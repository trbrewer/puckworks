# Reproduction

Base main: `4c5ebab5df79929813949df7113c21290dde40cc`.
The plan was committed before evaluations at
`8ffc63f0fdc54eab1daceccefed9be145d062667`.
No optimizer ran and no fit, historical artifact or production default changed.
EWP stayed read-only at `479783685360fdd31636890cf8e588a8fdd692d8`.

Use the scientific Python environment recorded in RUN_RECEIPT.json and separate
checkouts/evidence roots. The diagnostic is executed **as a script**, so its
inherited imports resolve exclusively from pinned #427. Do not use `python -m`:
mixing main's older hydraulic modules with #427's parameter adapter is rejected.
The #427 and #423 checkouts must have their exact heads and unchanged tracked
source/docs. Git objects for their inherited source pins must be present too.

```bash
export PYTHONDONTWRITEBYTECODE=1
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 NUMBA_NUM_THREADS=1
PY=/path/to/scientific/python
WORK=/path/to/new/external/diagnostics
mkdir -p "$WORK"
export NUMBA_CACHE_DIR="$WORK/numba-cache"
inputs=(
  --fade-code /path/to/checkout-at-ec0dc887ca0f66338fe166cd4ed8e7cbf2994441
  --fade-evidence /path/to/JOINT_MASS_FADE_001/external-evidence
  --ewp /path/to/read-only/ewp-form-a-001
  --native /path/to/FORM_A/campaign
  --raw /path/to/waszkiewicz/upstream
  --screen /path/to/WETTING_SCREEN_001/external-evidence
  --joint /path/to/JOINT_CLOCK_001/external-evidence
  --lc /path/to/LC_JOINT_TRANSFER_001/external-evidence
  --wasz /path/to/checkout-at-c4b4a07e110a3ede5013fd876a02a58ee6456eab
  --replay /path/to/checkout-at-ec82d1f019da3a5fcd9ff8748c29926c763d7bcc
  --work "$WORK" --workers 24
)
/usr/bin/time -v -o "$WORK/diagnostic-1-time.txt" \
  "$PY" puckworks/analysis/mass_fade_diagnostics_001.py "${inputs[@]}"
```

The fixed grid has 432 evaluations, plus 24 exact selected-vector checks.
GAMMA_SLICES.csv distinguishes `grid` and `selected` rows; components are the
inherited normalized objective contributions, whose sum is the total.
All common coordinates and fixed fold Mc are retained in each row. Counts
remain training counts for that fold, not held-out performance. START_VS_FINAL
joins each selected fade fit to its actual winning STARTS.csv record.
SLICE_SUMMARY retains all exact ties, local minima, neighboring grid values and
selected-minus-grid-minimum differences. No off-grid minimization is performed.

For a report-only change, use the authenticated saved evaluation cache:

```bash
/usr/bin/time -v -o "$WORK/report-1-time.txt" \
  "$PY" puckworks/analysis/mass_fade_diagnostics_001.py "${inputs[@]}" --report-from-cache
```

This mode checks the evaluation-file hash, every parameter vector and all input
identities before regenerating summaries/figures; it makes no objective calls.
This campaign used it once for plateau-tie classification and a linear plot
inset. Actual slices have unique grid minima, so the tie fix changed no result.
The original executed source is preserved externally as OBJECTIVE_SOURCE.py;
its hash is `objective_code_sha256`, separate from the final reporter's
`code_sha256`. The original evaluation cache stayed byte-identical. Both
commands completed successfully and are counted.

## Observation and resample contract

LATE_CHANGE_ORDERING.csv contains 56 per-brew rows and 11 condition rows.
Mass is recorded beverage scale mass, baseline-relative using #423's median
stable −2→0-s raw mass (first raw sample only if absent). +60/+100-s masses are
interpolated inside the exact retained native subset. They are neither filtered
flow integrals nor predicted liquid masses. Flow/pressure are the original
paired 2-s-window means. `achieved_pressure_bar` is the arithmetic mean of the
two matched window pressures; both components remain in the CSV.

Spearman uses eleven condition means. Every bootstrap draw resamples complete
brews within each of those fixed conditions, preserving mass/pressure/flow
pairing and recomputing both rank vectors. Shared bank SHA256:
`d599d80c854fd5a3cf9b9ca5d6fe1c617b222125bd1adcb36ad9edecd96801b6`.
Intervals are #423's finite-draw nearest-rank 2.5/97.5 percentiles, not normal
approximations. CORRELATIONS.csv also reports the paired difference of absolute
correlations. Elapsed duration is constant 40 s; its correlation is undefined,
not zero. No conditions are resampled, and no population or mechanism inference
is made. The eleven means share this one campaign.

## Authentication, compute and checks

INPUT_MANIFEST.json binds source heads, source-bundle hashes, original fitting
identity, the 24 fit JSON hashes, exact brew order and external freeze hashes.
The inherited source loader authenticates raw files, configurations, masks,
onsets and Mc, and reproduces all #423 windows before the new summaries.
VERIFICATION.json records 24 exact selected and 24 exact zero reproductions,
112 late windows, 56 mass/support/baseline checks and all eleven original paired
late-change intervals. All training objective/component/count comparisons use
exact equality; window/reference floating-point comparisons use rtol=atol=1e-12.

Actual scientific process-tree CPU was **0.0545417 core-hours**: 182.96 s for
the diagnostic and 13.39 s for the report-only pass, total 196.35 s. There were
zero failed scientific commands. External GNU `time -v` counts user+system CPU
including descendants; per-evaluation timers are not added again. Setup,
source inspection, QA, independent review and hosted CI are excluded. Timer,
code and output hashes and package versions are in RUN_RECEIPT.json. Large
intermediates stay outside Git in
`/home/tim/pw-mass-fade-diagnostics-001-evidence`.

```bash
PYTHONPATH=. "$PY" -m pytest -q tests/test_mass_fade_diagnostics_001.py
PYTHONPATH=. "$PY" -m ruff check puckworks/ tests/
PYTHONPATH=. "$PY" -c 'from puckworks.registry import run_all_gates; run_all_gates()'
git diff --check 4c5ebab5df79929813949df7113c21290dde40cc --
```

Local: 17 focused tests pass, including on minimum declared NumPy/SciPy
dependencies. The 31 inherited hydraulic tests pass (48 combined); registry is
66 PASS plus one acknowledged historical
exception. Unchanged base-suite evidence is reused from the prior task at this
same main SHA. Final-head required CI is linked in the draft PR. REVIEW.md
records the fresh read-only audit of claims. No successor.
