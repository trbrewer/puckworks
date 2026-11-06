# Reproduction

This is the declared **post-hoc reset exclusion** of #421, not an independent
prospective confirmation. Base: `65f51c63856677eccc4ba5a45ce555ea0c4eab99`.
The new branch is stacked against `pw-vis-predictor-001`. No source harvesting,
EWP writes, 001 bundle/model edits or production-default changes are involved.

The same permissioned July-15 Visualizer snapshot underlies both runs. Its source
aggregate SHA-256 is `6769656c8555d940bf79a2243a784c38b63066d3fe231227628667d251ba4d5b`;
inventory identity is `f46181ee8c461fab055b73511148dd26888c7c5b3cb1bc908aad6ab9db2bb766`.
The 001 manifest authenticated 465 source files. This rerun reads its frozen private
objects directly, preserving window values/roles and fold IDs. Parent cache hashes,
the filtered membership/window hashes and aggregate survivor-object hash are in
FROZEN_MANIFEST.json. No raw record or private path is published.

Use the final 001 execution runtime: Python 3.12.3, NumPy 2.0.2, SciPy 1.13.1;
Matplotlib 3.11.2 for figures. Install the checkout editable with dev/figures extras
and these explicit numerical pins. Set `FIT_PY` to that interpreter,
`VIS001_PRIVATE` to the authorized, read-only 001 cache directory, `VIS002_PRIVATE`
to a fresh owner-controlled directory outside Git, and `VIS002_OUTPUT` to
`docs/research/VIS_PREDICTOR_002` in this checkout. The runtime check intentionally
rejects a different NumPy/SciPy version for actual execution.

```bash
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1
"$FIT_PY" -m puckworks.analysis.vis_predictor_002 prepare \
  --private "$VIS002_PRIVATE" --parent-private "$VIS001_PRIVATE" --output "$VIS002_OUTPUT"
# This reproduces the already committed filtered manifest. Original freeze c866fea
# preceded every C0 score and fit; no fold generator is called.
"$FIT_PY" -m puckworks.analysis.vis_predictor_002 check-c0 \
  --private "$VIS002_PRIVATE" --parent-private "$VIS001_PRIVATE" --output "$VIS002_OUTPUT"
# STOP on a C0 discrepancy. The passing original receipt is committed at f6a82c4.
for fold in 0 1 2 3 4; do
  "$FIT_PY" -m puckworks.analysis.vis_predictor_002 fit --fold "$fold" --workers 8 \
    --private "$VIS002_PRIVATE" --parent-private "$VIS001_PRIVATE" --output "$VIS002_OUTPUT"
done
"$FIT_PY" -m puckworks.analysis.vis_predictor_002 deploy --workers 8 \
  --private "$VIS002_PRIVATE" --parent-private "$VIS001_PRIVATE" --output "$VIS002_OUTPUT"
"$FIT_PY" -m puckworks.analysis.vis_predictor_002 audit \
  --private "$VIS002_PRIVATE" --parent-private "$VIS001_PRIVATE" --output "$VIS002_OUTPUT"
"$FIT_PY" -m puckworks.analysis.vis_predictor_002 audit-deployment \
  --private "$VIS002_PRIVATE" --parent-private "$VIS001_PRIVATE" --output "$VIS002_OUTPUT"
"$FIT_PY" -m puckworks.analysis.vis_predictor_002 score \
  --private "$VIS002_PRIVATE" --parent-private "$VIS001_PRIVATE" --output "$VIS002_OUTPUT"
"$FIT_PY" -m puckworks.analysis.vis_predictor_002 export \
  --private "$VIS002_PRIVATE" --parent-private "$VIS001_PRIVATE" --output "$VIS002_OUTPUT"
"$FIT_PY" -m puckworks.analysis.vis_predictor_figures --output "$VIS002_OUTPUT"
python -m pytest -q tests/test_vis_predictor_001.py tests/test_vis_predictor_002.py
python -m pytest -q -m 'not slow and not live and not gpu and not external_data'
ruff check puckworks/ tests/
python -c "from puckworks.registry import run_all_gates; run_all_gates()"
```

The actual six fit invocations run concurrently with eight independent starts each,
one BLAS thread per worker, and serialized Design construction. All start schedules,
optimizer settings and the evaluator are unchanged. Public source hashes are in
CODE_HASHES.json; each saved model also records numerical/cohort/plan/fold identity,
runtime, original starts' status and process CPU. Resume accepts only matching 002
artifacts; a foreign/stale artifact is preserved privately and that declared model
is refitted. Existing released models can therefore reproduce predictions without
optimization. For fresh refits, use a throwaway checkout with its 002 model directory
moved aside; do not move or modify the 001 models. Floating-point reproducibility
is tied to the recorded runtime and exact saved-model hashes.

The mandatory C0 check recomputes predictions from surviving early windows through
the reusable API. It returns 1.2084042519074556 g/s RMSE and 1.6547408859936399 NRMSE,
with zero per-window discrepancy from the corresponding 001 cache. The tolerance
is 1e-9, declared before scoring the check. The check does not calibrate any shared
parameter or change any observation.

`score` creates one private cache and refuses to overwrite it. `report` uses the
authenticated cache to regenerate scores, bootstrap intervals, breakdowns, example
aggregates and matched-survivor comparisons, without refitting or rescoring models.
Cache identity includes all CV-model hashes; deployment models never enter it.
Both CV and deployment audits use the pinned independent complete-shot-batched
operator. Actual execution audits completed pressure models concurrently and then
assembles the same complete receipts; the serial commands above call the identical
operator. Audit failure stops scoring; the 1e-5 threshold is unchanged.

Use a saved model through `puckworks.empirical.visualizer.load_model` and `predict`
as documented in [001 reproduction](../VIS_PREDICTOR_001/REPRODUCE.md), replacing the
path with `VIS_PREDICTOR_002/models/deployment/M0R.json`.
RECOMMENDATION.json selects the model from primary cross-validation. Later query
windows need recorded pressure/current start mass for families using them; the
later target flow fields are ignored by the predictor. This is conditional window
prediction, not autonomous future-shot simulation.

ACCOUNTING.json separates CV and deployment optimizer core-hours and records
preparation, C0, audit and prediction CPU. Driver/design overhead, repeated hash
checks, reporting/bootstrap/comparison, figures, tests, review and hosted CI are
unmetered; recorded CPU is not a complete host-level total.

Raw records, salted linkage, individual errors and all cached predictions remain
outside Git. Public aggregates retain the same minimum-cell/complement/linkage
rules. Data source: Visualizer; thanks to the contributing users who made their
shots public. Research permission does not grant raw redistribution or endorsement.

The audited model set was committed at `d026df8f3b8d471b11a5b85e42ddcc6ffe4fff49`
before the single held-out scoring run. SCORING_RECEIPT.json binds that source
commit, the private prediction cache, audit receipts and released aggregate bytes.
Recorded CPU: 28.7128184713 core-hours for the 35 CV fits, 5.8926100076 for the seven
deployment fits, and 0.8939088588 for other recorded work; total 35.4993373378.
The concurrent fit batch took 0.9575078626 wall-hours. The accounting exclusions
above apply. No scientific or numerical settings changed after the 002 freeze.
