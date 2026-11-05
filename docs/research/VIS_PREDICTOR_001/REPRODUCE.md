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

Use Python >=3.10, `pip install -e '.[dev,figures,harvest]'`. Set `VIS_ROOT` to
the retained snapshot, `VIS_INVENTORY` to the existing owner inventory manifest,
and `VIS_PRIVATE` to a new owner-controlled directory outside the checkout.
No command below calls the Visualizer API.

```bash
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1
python -m puckworks.analysis.vis_predictor_001 prepare \
  --root "$VIS_ROOT" --inventory "$VIS_INVENTORY" --private "$VIS_PRIVATE"
# Inspect public funnel/manifest, run tests and the pre-score review; commit PLAN,
# FROZEN_MANIFEST, STARTS and FOLD_MANIFEST before fitting or scoring.
for fold in 0 1 2 3 4; do
  python -m puckworks.analysis.vis_predictor_001 fit \
    --private "$VIS_PRIVATE" --fold "$fold" --workers 4
done
python -m puckworks.analysis.vis_predictor_001 audit --private "$VIS_PRIVATE"
python -m puckworks.analysis.vis_predictor_001 score --private "$VIS_PRIVATE"
python -m puckworks.analysis.vis_predictor_001 deploy --private "$VIS_PRIVATE" --workers 4
python -m puckworks.analysis.vis_predictor_001 audit-deployment --private "$VIS_PRIVATE"
python -m puckworks.analysis.vis_predictor_figures
python -m pytest -q tests/test_vis_predictor_001.py
python -m pytest -q -m 'not slow and not live and not gpu and not external_data'
ruff check puckworks/ tests/
```

The five fold commands may run in separate processes; each start uses one BLAS
thread. Fits never share fitted starts between outer folds. Save each log outside
Git. Fit resume loads existing hashed model files. The `score` phase refuses to
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
Wall clock and summed process CPU accounting will be recorded in ACCOUNTING.json;
benchmark fits, deployment fits and numerical audit costs are separate. Tests,
interactive review, figure rendering and hosted CI are excluded/unmetered.

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
