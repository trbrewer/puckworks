# Reproduction

Only the existing permissioned July-15 Visualizer snapshot is used. Raw records,
source/user tokens, corpus membership, per-shot errors and held-out predictions
remain outside Git. Obtain authorized local access; public artifacts do not grant
raw redistribution rights. EWP and the snapshot are read-only.

Base: `4c5ebab5df79929813949df7113c21290dde40cc`.
Source-file aggregate SHA-256 (X1 authentication):
`6769656c8555d940bf79a2243a784c38b63066d3fe231227628667d251ba4d5b`.
Inventory identity: `f46181ee8c461fab055b73511148dd26888c7c5b3cb1bc908aad6ab9db2bb766`.
465 source files are authenticated against the retained inventory. These hashes
use X1's source-state definition; the earlier EWP programme's source/full-store
hashes use its own scope and are not substitutes.

For byte-identical extraction use the initial Python 3.12 / NumPy 2.5.4 /
SciPy 1.18.1 environment (`PREP_PY`). For continuation, scoring and figures use
Python 3.12 / NumPy 2.0.2 / SciPy 1.13.1 (`FIT_PY`). Install this checkout editable
and the dev/figures extras with those explicit dependency pins; the figures here
use Matplotlib 3.11.2. ENVIRONMENT.json
records both contexts and hashes of the 18 retained initial-runtime baselines and four retired pressure fits.
Set `VIS_ROOT` to
the retained snapshot, `VIS_INVENTORY` to the existing owner inventory manifest,
and `VIS_PRIVATE` to a new owner-controlled directory outside the checkout.
No command below calls the Visualizer API.

```bash
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1
"$PREP_PY" -m puckworks.analysis.vis_predictor_001 prepare \
  --root "$VIS_ROOT" --inventory "$VIS_INVENTORY" --private "$VIS_PRIVATE"
# The released PLAN/manifest are already committed. Preparation must reproduce
# their hashes exactly; a mismatch stops execution. The original authoring freeze
# was committed before any fitting or scoring.
for fold in 0 1 2 3 4; do
  "$FIT_PY" -m puckworks.analysis.vis_predictor_001 fit \
    --private "$VIS_PRIVATE" --fold "$fold" --workers 8
done
"$FIT_PY" -m puckworks.analysis.vis_predictor_001 audit --private "$VIS_PRIVATE"
"$FIT_PY" -m puckworks.analysis.vis_predictor_001 score --private "$VIS_PRIVATE"
"$FIT_PY" -m puckworks.analysis.vis_predictor_001 deploy --private "$VIS_PRIVATE" --workers 8
"$FIT_PY" -m puckworks.analysis.vis_predictor_001 audit-deployment --private "$VIS_PRIVATE"
"$FIT_PY" -m puckworks.analysis.vis_predictor_figures
python -m pytest -q tests/test_vis_predictor_001.py
python -m pytest -q -m 'not slow and not live and not gpu and not external_data'
ruff check puckworks/ tests/
```

The five fold commands may run in separate processes; a private lock serializes
verified Design construction, and each start uses one BLAS thread. Fits never share fitted starts between outer folds. Save each log outside
Git. Fit resume loads existing hashed model files. The released models therefore
reproduce the reported benchmark without refitting. To refit from scratch, use a
throwaway checkout and move its model directory outside the checkout before the
fit commands; fresh optimization may differ at floating precision across library
versions. The released hashes remain the exact reported-model authority. The `score` phase refuses to
overwrite cached predictions. `report` regenerates all aggregate tables from the
cache without refitting or rescoring models. Deployment artifacts never enter any
score/contrast. Independent audit checks their integration separately.

Reuse a saved predictor:

```python
from puckworks.empirical.visualizer import extract_windows, load_model, predict
windows, flags, reason = extract_windows(time_s, pressure_pa, weight_kg)
assert reason == "retained"
model = load_model("docs/research/VIS_PREDICTOR_001/models/deployment/T0.json")
early = [w for w in windows if w.role == "calibration"]
later = [w for w in windows if w.role == "score"]
flow_g_s, amplitude = predict(model, early, later)
```

Select the file named by RECOMMENDATION.json in actual use (T0 above is only an API
example). Query windows need their pressure history and observed start mass for
pressure/mass families. The later target flow fields are ignored by `predict`.
Extraction needs full support to form the benchmark; callers may also construct
Window covariates directly. This is conditional window prediction, not an
unobserved-future shot simulator.

Every saved model has a detached SHA-256; code, plan and corpus hashes are embedded
in its metadata. FROZEN_MANIFEST.json binds the private membership and windows.
Wall clock and summed process CPU accounting are recorded in ACCOUNTING.json;
benchmark fits, deployment fits and numerical audit costs are separate. Tests,
interactive review, figure rendering and hosted CI are excluded/unmetered.

Recorded CPU totals **55.858 core-hours**, including preserved failed versions.
The 35 final CV shared fits account for **23.871 core-hours**; the seven final
all-user deployment fits account for **5.301 core-hours**, separately from scoring.
Retired completed fits account for 20.451 core-hours. Other recorded costs include
interrupted workers, preparation, replay, numerical audits and prediction.
The final refined fit batch took 0.852 wall-hours; retained baselines came from
earlier execution. This is recorded process CPU, not a complete host-level total:
unreturned failed-audit worker CPU, some driver/startup work and report bootstrap
are also unmetered. ACCOUNTING.json gives the full allocation and exclusions.

The original plan/corpus freeze is commit
`24593a21bd7faf9a8aac84526c96424e98a711cb`; the forced numerical amendment is
`1bc130f`. Qualified saved models and all audit receipts were committed in
`40cd886` before the first held-out scoring invocation. Score computation used
the runner/core hashes recorded in SCORING_RECEIPT.json; CODE_HASHES.json binds
the final released code. Subsequent publication corrections additionally suppress
unsafe contributor-user transitions, break lines across suppressed bins and label
a symmetric-log axis. They change neither cached predictions nor scored aggregates.

Data source: Visualizer; thanks to the contributing users who made their shots public.

Prior-work readings: X1, COR15 and Form A/D0/JOINT_CLOCK are the unchanged files at
this task's Puckworks base. The EWP private-work record was read without writes at
EWP commit `73591dd27cd5707749713b1eb28042d356463786`, file SHA-256
`04776d834668eefcc3b2e6fca7ed582ab8e8a8803791b44b57c8bef7b1a23f27`.
[PR #419](https://github.com/trbrewer/puckworks/pull/419) was read at head
`90c7d6fea8ade41891f83ab96d47b675bb18d3e3`;
[PR #420](https://github.com/trbrewer/puckworks/pull/420) at
`faa8715951ad7987baa5f54503a2c8bc733f356e`. Neither PR's qualification result is
recast as an empirical-admission failure. The benchmark runner uses POSIX fork
workers; the reusable extraction, model and prediction API needs only core NumPy/SciPy.

A fresh private extraction at the continuation code reproduced both frozen
corpus/fold and window-cache hashes byte-for-byte. `prepare` preserves the original
base identity when verifying an existing frozen manifest, and rejects a mismatch.
Failed runtime attempts, unchanged-score replays and the eventual exact-hash
lookup repair are recorded in DEVIATIONS.md. No numerical threshold was retuned.

The final operator evaluates pressure means in log space and direct LS in compensated
extended precision. Linux x86 extended precision was used for this benchmark. Numeric
range can be smaller on other platforms; unrepresentable trials raise or fail
explicitly. A returned physical amplitude can be infinite even when the normalized
predicted flow is finite; use the returned predictions, not a raw amplitude product.

Following the preserved pre-score integration failure, pressure-model evaluation
subdivides original linear native intervals to at most 0.1 bar pressure change,
using GL16 in each piece with the original time weights. Saved artifacts bind this
method in `integration.max_pressure_step_bar`; `None` reproduces legacy native
GL16. The independent audit stays on original intervals (GL64 plus adaptive).
The extraction cache and corpus/fold hashes are unchanged. See the numerical
amendment in PLAN.md and failure record in DEVIATIONS.md. The amended operator
remains subject to the same 1e-5 selected-model audit; it is not a uniform accuracy
guarantee over unbounded n.

Execution concurrency was eight independent optimizer starts per fold in the
refined run, with serialized Design construction and one BLAS thread per worker.
The 18 retained baseline artifacts originated with four workers and replay under
the corrected operator. Actual model audits ran concurrently as artifacts became
available, calling the same published `audit_quadrature` operator; the serial
`audit` commands above reproduce the same numerical checks.

The final audit uses batches of complete shots to limit temporary arrays after
an execution indexing failure. Calibration normalization stays within each complete
shot; the mathematical check and 1e-5 threshold are unchanged. All 42 selected
training objectives replay under the added ownership/time-weight guards, with
maximum discrepancy 2.274e-13 g/s. The root cause of the execution failures remains
unresolved; preserved failures and accounting limits are in DEVIATIONS.md.
