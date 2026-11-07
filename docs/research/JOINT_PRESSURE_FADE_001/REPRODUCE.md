# Reproduction

Python >=3.10, repository development dependencies, Numba and Matplotlib.
Run from this checkout; originals, native configurations, source fit JSON,
new predictions and trial histories stay outside Git. EWP is read-only.

```bash
export PYTHONPATH=.
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 NUMBA_NUM_THREADS=1
PY=/path/to/environment/bin/python
WORK=/path/to/external/pressure-fade-evidence
inputs=(
  --ewp /path/to/read-only/ewp-form-a-reference
  --native /path/to/FORM_A/campaign
  --raw /path/to/waszkiewicz/upstream
  --screen /path/to/WETTING_SCREEN_001/artifacts
  --joint /path/to/JOINT_CLOCK_001/artifacts
  --lc /path/to/LC_JOINT_TRANSFER_001/artifacts
  --wasz /path/to/checkout-at-c4b4a07e110a3ede5013fd876a02a58ee6456eab
  --replay /path/to/checkout-at-ec82d1f019da3a5fcd9ff8748c29926c763d7bcc
  --fade-evidence /path/to/JOINT_MASS_FADE_001/artifacts
  --work "$WORK"
)
mkdir -p "$WORK"
"$PY" -m pytest -q tests/test_joint_pressure_fade_001.py tests/test_joint_mass_fade_001.py tests/test_joint_clock_001.py tests/test_wetting_screen_001.py tests/test_mass_fade_diagnostics_001.py
/usr/bin/time -v -o "$WORK/reference-time.txt" "$PY" -m puckworks.analysis.joint_pressure_fade_001_run reference "${inputs[@]}" --workers 12
/usr/bin/time -v -o "$WORK/fade-time.txt" "$PY" -m puckworks.analysis.joint_pressure_fade_001_run fade "${inputs[@]}" --workers 96
/usr/bin/time -v -o "$WORK/evaluate-time.txt" "$PY" -m puckworks.analysis.joint_pressure_fade_001_evaluate "${inputs[@]}" --workers 32
/usr/bin/time -v -o "$WORK/report-time.txt" "$PY" -m puckworks.analysis.joint_pressure_fade_001_report "${inputs[@]}"
```

The plan/start bank were committed at `12887ba`; the pre-fit implementation and
independent audit at `641d630`. The runner checks the plan/bank are committed and
the reference reproduction matches the current fitting identity before fitting.
Exactly 12 problems and 19 starts each; no control refit. The first four starts
are the matching #427 refreshed vector at gamma_P*1300=0,.05,.15,.30. The
remaining fifteen reuse #427's common-parameter LHS vectors exactly and add the
one-dimensional LHS coordinate (seed 20261107). START_BANK freezes the vectors;
STARTS records initial/final coordinates, objective values, retained minima and
trial hashes. Powell uses inherited tolerances and no iteration/evaluation cap.
Best-finite retention includes starts and intermediate points, even when the
returned endpoint is worse. Failed attempts must be preserved and accounted
before retry; changed fitting identities cannot resume prior starts.

The reference command re-evaluates all twelve reused controls at .02 s and
requires exact equality of objective, both components, condition contributions
and training detection counts. The inherited loader authenticates original
brews, native configurations, fixed masks/onsets, fold membership and Mc.
INPUT_MANIFEST binds #427 compact artifacts and large frozen fits; Git objects
authenticate pinned source code. #428's slice helper is also checked against its
pinned commit. No historical files are overwritten.

The two hydraulic paths independently integrate Phi using the clipped line
pressure and trapezoidal step increment, with old/mid/new exposure in their
corresponding updates. Their water masses and flows must agree. The midpoint
water increment drives the unchanged conservative chemistry. Focused analytical
tests additionally check the separable constant-pressure mass integral and
pressure exposure; zero/mass-fade source functions were independently compared
against #427 by the pre-fit reviewer.

Replay freezes all 48 parameter vectors (36 reused, 12 newly fitted), then
evaluates 448 arm/scope/brew cases at .02 and .005 s. The same #424 native observer
and windows are applied to beverage, liquid and solute cumulative masses; the
split must reconstruct total. All inherited arm windows, detectors and errors
are compared exactly with #427's retained evaluation. #424 levels and #425
contributions are separately checked at rtol=atol=1e-12. The actual rig's split
is not identified.

Trajectory intervals use the exact 1,000 whole-brew-within-condition bank,
SHA256 `d599d80c854fd5a3cf9b9ca5d6fe1c617b222125bd1adcb36ad9edecd96801b6`.
Inherited J1 aggregate RMSE intervals use its separate condition-then-brew bank,
seed 20261103, verified against the retained file. The ALL score is the inherited
mean of condition RMSEs. Onset rows retain intended/available/detected counts;
differences involving computed censor bounds are not bounds on the difference
of unknown true errors. All intervals condition on the frozen vectors/Mc.

GAMMA_P_SLICES contains exactly 132 fixed grid evaluations plus 12 selected-vector
checks, all at .02 s. Every coordinate other than gamma_P stays fixed. Selected
rows reproduce saved objectives/components/counts exactly; zero grid rows match
the fixed-parameter gamma-zero diagnostics. SLICE_SUMMARY uses #428's exact
discrete classification without a flatness threshold, retains grid minima and
gaps, and reports whether the selected point is bracketed and no worse than its
adjacent grid points. Coarse slices are not profile likelihoods, joint
convergence proofs, or evidence that an off-grid selected value is stationary.

PEAKS reports native-observer maxima, exact ties, boundaries, local maxima and
explicit horizons, for each brew and equal-brew condition means on common
support. Boundary-only global maxima are labelled "no interior peak within
horizon"; flat curves have no unique maximum. FADE_FACTORS reports
exp(-gamma_P*P*40) for each fit at every constant nominal pressure, plus actual
post-breakthrough recorded exposure increments over stable +60→100 s.
FLOW.svg displays 4/6/9/11/13-bar observed and all-arm beverage flow at .005 s;
LOCO and DESCRIPTIVE_ALL stay separate. VIZ_SPEC documents the encodings.

Required checks:

```bash
"$PY" -m pytest -q -m 'not slow and not live and not gpu and not external_data'
"$PY" -m ruff check puckworks/ tests/
"$PY" -c 'from puckworks.registry import run_all_gates; run_all_gates()'
git diff --check fa0b14003cb0d7c77a902e3adf1e6fd1a38bf120 --
```

Scientific compute uses external GNU time user+system CPU for the process tree,
including every scientific command and failure; per-start timers are not added
again. Setup, focused QA, independent review and hosted CI are separate. Large
evidence is retained under `/home/tim/pw-joint-pressure-fade-001-evidence`.
Final actuals, timer hashes, package versions and artifact hashes are recorded
in RUN_RECEIPT.json after completion. No successor.
