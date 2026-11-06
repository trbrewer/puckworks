# Reproduce the saved-array decomposition

Base: `4c5ebab5df79929813949df7113c21290dde40cc`. The input manifest, plan and
unchanged observation helper were committed before decomposition at
`d2d3c21c23a73130f8ac1b4db9794cf85963afae`.

Read-only references:

- #424: `ec82d1f019da3a5fcd9ff8748c29926c763d7bcc`.
- #423: `c4b4a07e110a3ede5013fd876a02a58ee6456eab`.
- EWP remains unchanged at `479783685360fdd31636890cf8e588a8fdd692d8`;
  this postprocessor does not need to load or execute EWP.

Use the inherited model observation environment: Python 3.12.3, NumPy 2.2.6,
SciPy 1.18.1 and Matplotlib 3.11.2. Numba/model evaluation is not used by this
runner. Execute from this checkout so its local package is imported. Do not
invoke the historical reference/replay CLIs.

```bash
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 NUMBA_NUM_THREADS=1
MODEL_PY=/path/to/inherited/runtime/bin/python
REPLAY=/path/to/read-only/424-checkout
WASZ=/path/to/read-only/423-checkout
RETAINED=/path/to/retained/TURNOVER_TIME_REPLAY_001/private
RAW=/path/to/zenodo-18046315/upstream
PRIVATE=/path/to/fresh/TURNOVER_REPLAY_DECOMPOSITION_001/private
OUTPUT=/tmp/turnover-replay-decomposition-output

"$MODEL_PY" -m puckworks.analysis.turnover_replay_decomposition_001 \
  --replay "$REPLAY" --wasz "$WASZ" --retained "$RETAINED" \
  --raw "$RAW" --private "$PRIVATE" --output "$OUTPUT"

python -m pytest -q tests/test_turnover_replay_decomposition_001.py
ruff check puckworks/ tests/
python -c 'from puckworks.registry import run_all_gates; run_all_gates()'
```

`INPUT_MANIFEST.json` contains every retained NPZ filename/SHA-256, pinned public
source hashes, exact brew order, source-observer function hash and the retained
index hash **3ab272e46fb7445722c8dd4057f4e05f5ebe8473d971d6bead89b5280e00af3e**.
The index's code, plan, input and saved-window identities are cross-checked with
#424's public receipt. #424 retained each NPZ hash in that private index; it did
not separately publish the index file hash. This task freezes that existing
index file as an input and authenticates every NPZ against its original entry.
All public #424 totals and per-window totals provide additional reconstruction
checks. No retained artifact is modified or regenerated.

The retained producer defines `liquid_g` as its predicted cumulative liquid
mass and `solute_g` as cumulative discharged solute, in grams;
`beverage_g = liquid_g + solute_g`. `stored_solute_g` is internal inventory,
not discharged solute. The postprocessor requires both separate saved signals;
it cannot substitute subtraction from the total or run a model to recover them.

`wasz_turnover_time_001.py` is copied byte-identically from #423/#424
(SHA-256 **9b59fec8611d0465e5dc0f19a5837565d1a3c3b9dbb997b6886b76476815656d**).
`beverage_observer` has exactly #424's function source and is checked against its
pinned source before use. For each signal: interpolate cumulative mass onto the
same clean native timestamps, differentiate with `numpy.gradient`, apply the
31-sample order-one Savitzky–Golay filter, then use the unchanged piecewise-linear
2-s paired-window integral. This is a window contribution from the mass observer,
not the retained instantaneous `bed_flow_g_s`. Full support includes the 99–101-s
window and the native derivative/filter support. Observed onset anchors both
signals on onset-clock rows. No detector selection, lag, clipping or fitting mask
is introduced. All 56 raw-source hashes, native observations, recorded achieved
window pressures, boundaries and availability reproduce the pinned observations.

The exact shared 1,000-draw bank has SHA-256
**d599d80c854fd5a3cf9b9ca5d6fe1c617b222125bd1adcb36ad9edecd96801b6**.
Both the complete brew order and hash are checked. Whole brews are resampled
within nominal condition, and each draw index is reused across components and
times. For late changes, subtract the +60-s mean from the +100-s mean *within
each draw*, then take inherited nearest-rank pointwise 95% intervals. Interval
endpoints are not subtracted or added. These intervals are conditional on the
frozen parameters and Mc, without simulation or refit uncertainty.

Outputs:

- `CONTRIBUTIONS_BY_TIME.csv`: 440 model/scope/condition/time/clock rows, equal-
  brew liquid/solute/total means, observed beverage mean and achieved pressure.
- `PHASE_CONTRIBUTIONS.csv`: 36 rows for 9/11/13 bar and stable 10→40, 40→60,
  60→100 s; signed changes in g/s with observed changes beside them. The 60→100
  rows include paired intervals for all components and observed total. Blank
  earlier-phase interval cells mean not requested, not zero or missing support.
- `SLOPE_CONTRIBUTIONS.csv`: 40 rows of the unweighted slope across the three
  nominal 9/11/13 condition means, against their same achieved window pressures.
  The pressure coordinate is identical for all components, making the slope
  additive too. LOCO slopes combine different held-condition fits; descriptive
  slopes use one common in-sample parameter set.
- `FLOW_DECOMPOSITION.svg`: four model/scope rows by three high-pressure columns,
  stable-clock component areas and observed beverage flow. Connections guide
  the eye; the table retains both clocks. Negative contributions, if present,
  are drawn below zero rather than clipped. See `VIZ_SPEC.json`.

`RUN_RECEIPT.json` authenticates source/output hashes and records reconstruction:
224 arrays, 2,240 windows; saved cumulative mass sum residual **0 g**, total-mass
observer versus #424 residual **0 g/s**, separate-component window residual at
most **3.5971e-14 g/s**, condition-mean residual **1.1990e-14 g/s**, slope residual
**2.3176e-15 g/s/bar**, all within `rtol=atol=1e-12`. Every bootstrap draw's total
is checked too. Any reconstruction failure stops before public aggregate output.
The per-brew/window audit stays in the fresh private output location.

Measured main-command compute: **0.00126455 CPU core-hours** (4.55237192 CPU s),
covering authentication, observation postprocessing, aggregation and figure
generation. Initial input inspection, imports, preview/review, tests and hosted
CI are outside this measurement; it is not total host usage. **Zero simulations
and zero fits.** The first synthetic test used an overly tight analytic-quadratic
comparison for non-aligned linear-interpolation nodes; its approximation tolerance
was corrected before decomposition. The frozen `1e-12` reconstruction tolerance
and all scientific settings remained unchanged.

Attribution: Waszkiewicz et al., [Zenodo 18046315](https://doi.org/10.5281/zenodo.18046315),
CC-BY-4.0. The observed beverage mass has no measured liquid/solute split here;
the decomposition concerns model bookkeeping only and establishes no mechanism
or physical validation. No production, historical-result or EWP changes.
