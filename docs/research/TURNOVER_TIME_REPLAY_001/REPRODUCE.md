# Reproduction and observation identities

Base: `4c5ebab5df79929813949df7113c21290dde40cc`. The plan, input manifest and
byte-identical #423 observer were committed before new outcomes at
`25dcf944c7132b08df06f3c237aaa89f6359b4ef`. The reference checkouts are read-only:

- Waszkiewicz #423: `c4b4a07e110a3ede5013fd876a02a58ee6456eab`.
- Visualizer #422 compatibility head: `d4386441fbc387c0a83219817dac6f4bce3b94a3`.
- EWP checkout: `479783685360fdd31636890cf8e588a8fdd692d8`; its inherited FORM_A
  manifest and original configurations, not its branch name, authenticate inputs.

No original, historical bundle, saved fit or production default is modified.
The required unmerged data are read from those explicit checkouts; #421–#423
need not be merged. No optimizer runs. A-J1 is the saved J1 λ=1 family; the other
new beverage comparison is explicitly D0's **diagnostic fresh-bed R0 wrapper**.

## Environments and commands

`MODEL_PY` is Python 3.12.3 with NumPy 2.2.6, SciPy 1.18.1, Numba 0.68.1 and
Matplotlib 3.11.2, matching JOINT_CLOCK's inherited manifest. `VIS_PY` uses
Python 3.12.3 / NumPy 2.0.2 / SciPy 1.13.1, matching the retained Visualizer
runtime. Install this checkout in those research environments, or invoke
`python -m` from its root so the local package is used. Use fresh private output.

```bash
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 NUMBA_NUM_THREADS=1
MODEL_PY=/path/to/model-runtime/bin/python
VIS_PY=/path/to/visualizer-runtime/bin/python
EWP=/path/to/read-only/espresso-whole-pull
RAW=/path/to/zenodo-18046315/upstream
NATIVE=/path/to/retained/FORM_A/campaign
SCREEN=/path/to/retained/WETTING_SCREEN_001/evidence
JOINT=/path/to/retained/JOINT_CLOCK_001/evidence
WASZ=/path/to/pinned/423-checkout
VIS=/path/to/pinned/422-checkout
VIS_PRIVATE=/path/to/retained/VIS_PREDICTOR_002/private
PRIVATE=/path/to/fresh/TURNOVER_TIME_REPLAY_001/private
OUTPUT=/tmp/turnover-time-replay-output

ARGS=(--ewp "$EWP" --raw "$RAW" --native "$NATIVE" --screen "$SCREEN"
      --joint "$JOINT" --wasz "$WASZ" --private "$PRIVATE" --output "$OUTPUT" --workers 4)
"$MODEL_PY" -m puckworks.analysis.turnover_time_replay_001 reference "${ARGS[@]}"
"$MODEL_PY" -m puckworks.analysis.turnover_time_replay_001 replay "${ARGS[@]}"
# Later reporting reuses authenticated saved predictions; no new simulations:
"$MODEL_PY" -m puckworks.analysis.turnover_time_replay_001 report "${ARGS[@]}"
"$VIS_PY" -m puckworks.analysis.turnover_time_replay_001_coverage \
  --vis "$VIS" --vis-private "$VIS_PRIVATE" --private "$PRIVATE" --output "$OUTPUT"

python -m pytest -q tests/test_turnover_time_replay_001.py
ruff check puckworks/ tests/
python -c 'from puckworks.registry import run_all_gates; run_all_gates()'
```

The runner authenticates original hashes/configurations and source onsets with
the inherited read-only loader. All 56 observed traces reproduce #423's window
values and availability. The copied observer's SHA-256 is
`9b59fec8611d0465e5dc0f19a5837565d1a3c3b9dbb997b6886b76476815656d`.
The Visualizer reader authenticates `windows.pkl` and `corpus-folds.json` before
decoding into passive containers; it preserves the stored mean-pressure dot
product, role, timing and membership, without importing an unmerged fitter.

## Historical prerequisites and new comparison

`HISTORICAL_REPRODUCTION.csv` has **317 passing rows**: 79 A-J1 cases at each
of two steps, 79 D0 diagnostic-wrapper cases at each step, and the original D0
fixture replay. The 79 cases are 56 held-condition brews plus 23 saved constant
pressures. State arrays, instantaneous liquid endpoints/traces and detector
outputs are replayed at the original 0.02/0.005-s conventions. Joint/screen
tolerance is the inherited `rtol=atol=1e-12`; original D0 uses `rtol=1e-12,
atol=0`. The original D0 case rechecks all twelve point-bank brew records and
its saved endpoint/trace metrics on its original grids and masks.

These reference identities are separate from the new 224 measured-history
beverage replays. In particular, a new 99–101-s beverage mean is not compared
for equality with a historical instantaneous liquid endpoint or a historical
constant-pressure DESCRIPTIVE_ALL output.

The inherited general-horizon predictor uses 0.005 s / 256 cells through the
genuine native clean end. Its original normalized measured-pressure forcing
through 100 s is extended only with clean recorded pressure beyond 100 s,
as in JOINT_CLOCK. The D0 arm uses Z's fully wet initial state, M=0, fresh R0
inventory and zero dissolved solute. There is no observed-mass/TDS state input.

Predicted beverage mass B=M+outlet solute is sampled at #423's native clean
timestamps before the inherited gradient and 31-sample, order-one filter.
The unchanged paired-window integration then averages the 2-s centered window.
Observed onset aligns **both** signals on onset rows. The predicted detector
uses its separate inherited native 0–100-s support; 12 non-detections remain
in the comparison. `DETECTOR_ONSETS.csv` distinguishes non-detection from
unavailable predictions. All 2,240 attempted windows are available; their
private record file and every private prediction array are hash-bound in the
execution receipts. Aggregate support is in `AVAILABILITY.csv`.

## Tables, resampling and internal diagnostics

`PREDICTED_BY_TIME.csv` contains 440 model/scope/time/condition rows, including
observed and predicted beverage-flow means, paired differences and internal
states. `SLOPE_COMPARISON.csv` contains the unweighted nominal-9/11/13-condition
slope using #423's **recorded window-mean achieved pressure for both signals**.
LOCO combines different held-condition fits; DESCRIPTIVE_ALL is one common
in-sample vector. Maxima are among condition means, not located peaks. Exact
ties and available-edge/missing-condition flags are retained. At all-zero
prediction windows, every condition ties and the 13/max ratio is undefined.

`TRAJECTORIES_9_11_13.csv` distinguishes `snapshot`, the three requested `phase`
increments, and `adjacent` changes. An increment is later minus earlier flow,
in g/s, not a mass increment or time derivative. `9_minus_13` subtracts those
two flow increments. Observed-minus-predicted contrasts use identical draw IDs.
Stable-100-minus-current slope changes explicitly use the stable-pressure
reference for onset-clock rows; there is no onset-100-s observation.

The exact #423 brew order is in `RUN_RECEIPT.json`. Reconstructed draw-bank
SHA-256 must equal **d599d80c854fd5a3cf9b9ca5d6fe1c617b222125bd1adcb36ad9edecd96801b6**,
not merely share seed 20261106. There are 1,000 within-condition whole-brew draws,
shared across both signals, every model/scope and every time/clock. Intervals are
nearest-rank pointwise 95%, conditional on saved parameters and Mc. Missing
predictions never become zero or silently reduce an observed condition.

`PARAMETER_BANK.json` records the 24 model/fold vectors. Parameter order is
`a, Pstar, n, Pd` with `tau0` appended for A-J1; Mc is separately named and
matched to each fold. Source fit/manifest/parameter hashes are in the input and
run receipts. Internal C(P) includes the inherited amplitude; predicted liquid
M and R(M) are recorded on the integration grid, interpolated to native nodes,
time-averaged in each window, then averaged equally across its brews. Liquid
flow is labeled separately from the beverage derivative. These means do not
factor the mean of C×R or uniquely identify recovery's contribution.

## Visualizer disclosure and accounting

`VIS_HIGH_PRESSURE_COVERAGE.csv` releases only the independent all-score total:
118,542 windows, 10,231 shots and 315 users. All six requested pressure cells,
including the below-9 complement, are `whole_partition_withheld`; empty CSV
cells are **withheld**, not zero. No bin percentage, count, contributor total or
time summary is released, and no substitute coarsened above-10 aggregate is
introduced. The frozen 20-shot/10-user, complement and contributor-linkage
checks apply before any public row is written. Counts of shots/users would
overlap bins and cannot be summed as distinct totals. Detailed counts, timing,
linkage and release audits stay outside Git. Coverage does not establish
detection power; no aggregate AR gain does not imply no fitted downturns.

Recorded compute is **0.045669 CPU core-hours**: part A **0.044919** and part B
**0.000749**. It includes three historical-check executions (317 unchanged
checks each), one 224-case new replay, final reporting and the census. Earlier
historical checks were retained while unavailable-output handling/accounting
was completed and an unused import removed; no model, observation, numerical
setting or scientific comparison was tuned. Their private receipts are archived
and counted. Final reference/replay receipts separate parent and worker CPU to
avoid double counting; the earliest check records original-replay/worker CPU
only, excluding its loader/driver overhead. Imports, tests, review, setup and
hosted CI are outside these measured phases; this is not total host usage.

Attribution: Waszkiewicz et al. (2025), [Zenodo 18046315](https://doi.org/10.5281/zenodo.18046315),
CC-BY-4.0 data. Credit Visualizer and contributing users for the permissioned
public-shot corpus. Raw redistribution, endorsement, physical validation and
cross-corpus agreement are not implied. No successor is started.
