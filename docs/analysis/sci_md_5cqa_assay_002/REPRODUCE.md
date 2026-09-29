# Reproduction and saved inference

The three saved research models use only local NumPy/SciPy inference. Loading,
conditioning, independent interval queries and requested-stop delivery require no
original source files, private evidence, network access or optimizer. The runtime
is `puckworks.analysis.early_assay_5cqa_delivery`. Inputs are strict frozen
`L1MInput`, `L2MInput` and `L12Input` schemas, with masses in kg and exact 5CQA
interval-average concentrations in kg/kg. Convert mg/g using
`assay_from_mg_g`; percent is rejected. L2M requires the first vial's mass.

```bash
export PYTHONPATH=.
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
python docs/analysis/sci_md_5cqa_assay_002/synthetic_saved_model_example.py
```

That example saves and reloads explicitly synthetic models for all three
contracts. For a retained fitted model:

```python
from puckworks.analysis.early_assay_5cqa_delivery import Model, L2MInput, State
model = Model.load('docs/analysis/sci_md_5cqa_assay_002/models/L2M.json')
state = model.condition(L2MInput(.004, .006, .002, input_class='SYNTHETIC'))
intervals = state.predict_intervals([.01, .03], [.03, .05])
remaining = state.remaining_5cqa(.06)
assert State.from_dict(state.to_dict()) == state
```

These are illustrative supplied inputs, not a measured source shot. Predictions
return species kg/mg, interval-average mg/g, numerical allowance, support and
feature extrapolation. Independent queries neither refit nor affect each other.
Remaining means modeled delivery from the common anchor to the supplied stop,
not remaining puck inventory. Query mass is supplied, not hydraulically predicted.

## Single retained scientific execution

The task used the existing registered Pannusch resolver and existing environments
(Python 3.12.3, NumPy 2.5.3, SciPy 1.18.1). No dependency installation or lock change
was needed. Resolve the actual private task directory through the registered
source configuration; no local absolute path is published:

```bash
SOURCE_ROOT="$(python - <<'PY'
import json, os
from puckworks.analysis.pannusch_mass_delivery import config_path
print(os.environ.get('PUCKWORKS_EXTERNAL_DATA_ROOT') or
      json.loads(config_path().read_text())['sources']['PANNUSCH2024_MENDELEY_FULL_REPOSITORY']['path'])
PY
)"
TASK_EVIDENCE_ROOT="$SOURCE_ROOT/5cqa-assay-002-evidence-20260929T163451Z"
EVIDENCE_ROOT="$TASK_EVIDENCE_ROOT/run-001"
REVIEW_RECEIPT="$TASK_EVIDENCE_ROOT/review/review.json"
RUNNER=puckworks.analysis.pannusch_early_assay_5cqa_delivery
python -m "$RUNNER" prepare --out "$EVIDENCE_ROOT"
python -m "$RUNNER" develop --out "$EVIDENCE_ROOT"
python -m "$RUNNER" freeze --out "$EVIDENCE_ROOT"
python -m "$RUNNER" score --out "$EVIDENCE_ROOT" --review "$REVIEW_RECEIPT"
python -m "$RUNNER" verify --out "$EVIDENCE_ROOT"
python -m "$RUNNER" report --out "$EVIDENCE_ROOT"
```

The first four forms document the single authorized execution. They are not
rerun instructions. Prepare requires a fresh directory; the task binds one run
location, persistent clocks and attempt receipts; freeze requires a clean committed
producer; score requires the independently supplied approval and rejects any prior
score receipt, outcome artifact or completed score. The actual six-hour deadline
is fixed at 2026-09-29T22:34:51Z from the 16:34:51Z task start. Never change that
clock or create another directory to evade limits.

Only verify/report are repeatable after completion. Verify checks frozen source
register, code, model and private artifact identities and replays saved inference;
it performs no fitting or new outcome join. Report checks the retained completion
and reads existing scores without rescoring. Public saved inference remains usable
after the task deadline. Full private verification requires the retained evidence
and producer Git object; it needs no original workbooks. Full scientific execution
requires original registered files and the retained #299 reference archive, whose
identities are checked without invoking its scorer. Rights-restricted originals,
observations, predictions, shot results, actual commands/environments and logs stay
outside Git. Source-derived models/results retain Pannusch/Schmieder CC-BY-NC-3.0,
Mendeley DOI 10.17632/y2tz67f6ry.1, separately from software licensing.
