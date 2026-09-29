# Execution and reproduction

SCI-MD-5CQA-DELIVERY-001; G1; NO_GOVERNING_PHYSICS_CHANGE; RESEARCH_ONLY.
Run from the Puckworks checkout using the recorded Python 3.12.3 / NumPy 2.5.3 /
SciPy 1.18.1 environment. Original source stages additionally require openpyxl.
The configured resolver supplies the original corpus; no download or replacement
lineage is used. The private continuation README records exact local executables.

Resolve the already-used task locations from the existing source configuration:

```bash
export PYTHONPATH=.
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
SOURCE_ROOT="$(python - <<'PY'
import json, os
from puckworks.analysis.pannusch_mass_delivery import config_path
print(os.environ.get('PUCKWORKS_EXTERNAL_DATA_ROOT') or
      json.loads(config_path().read_text())['sources']['PANNUSCH2024_MENDELEY_FULL_REPOSITORY']['path'])
PY
)"
TASK_EVIDENCE_ROOT="$SOURCE_ROOT/5cqa-delivery-001-evidence-20260928T191319Z"
EVIDENCE_ROOT="$TASK_EVIDENCE_ROOT/run-001"
REVIEW_RECEIPT="$TASK_EVIDENCE_ROOT/continuation/review/review.json"
```

The first four commands below record the single authorized execution. They are
not replay commands: prepare refuses an existing directory, fitting has durable
exclusive counters, freeze binds immutable artifacts, and score refuses a prior
score or failed score receipt. The real authorization deadline is enforced.
Do not create a new directory to evade the retained counters or repeat the score.
The independent receipt is produced by the reviewer, never the implementer.

```bash
python -m puckworks.analysis.pannusch_conditional_5cqa_delivery prepare --out "$EVIDENCE_ROOT"
python -m puckworks.analysis.pannusch_conditional_5cqa_delivery develop --out "$EVIDENCE_ROOT"
python -m puckworks.analysis.pannusch_conditional_5cqa_delivery freeze --out "$EVIDENCE_ROOT"
python -m puckworks.analysis.pannusch_conditional_5cqa_delivery score --out "$EVIDENCE_ROOT" --review "$REVIEW_RECEIPT"
python -m puckworks.analysis.pannusch_conditional_5cqa_delivery verify --out "$EVIDENCE_ROOT"
python -m puckworks.analysis.pannusch_conditional_5cqa_delivery report --out "$EVIDENCE_ROOT"
```

Only `verify` and `report` are repeatable read-only reproduction stages. `verify`
checks exact code/model/source-register/artifact identities and replays saved-model
inference without fitting, target joins or rescoring. `report` checks retained
score/completion bindings and reads the existing aggregate score. Originals and
row-level artifacts stay private; public models are sufficient for new supported
mass-only API queries without a source workbook or predecessor execution directory.

## Saved-model research API

This example uses illustrative masses, not an experimental observation. For a
real query supply the measured first and second original vial masses and cumulative
mass coordinates including intervening unassayed vials. Units are kg throughout
inputs; no chemical assay or recipe feature is accepted.

```python
from pathlib import Path
from puckworks.analysis.conditional_5cqa_delivery import Model, EarlyInput

models = Path('docs/analysis/sci_md_5cqa_delivery_001/models')
for arm in ('E0', 'D0'):
    model = Model.load(models / f'{arm}.json')
    state = model.condition(EarlyInput(arm, (0.004, 0.006), 'SYNTHETIC'))
    for delivery in state.predict_intervals([0.02, 0.04], [0.03, 0.05]):
        if not delivery.numerical_qualified:
            raise ValueError('Interval exceeds the fixed numerical allowance')
        print(arm, delivery.species, delivery.five_cqa_kg,
              delivery.five_cqa_mg, delivery.five_cqa_mg_g,
              delivery.allowance_kg, delivery.support,
              delivery.feature_extrapolation, delivery.model_sha256)
    remaining = state.remaining_5cqa(0.06)
    assert remaining.numerical_qualified
```

The upper mass support is 0.06971540000000001 kg. Queries before m1+m2 or above
support fail. Zero-width intervals return zero analyte mass and undefined average
concentration. Feature extrapolation is visible and is not a favorable exclusion;
extreme allowed coefficients with extrapolated features may fail numerical
qualification. Check that flag. Modeled unassayed gaps are not measured whole-cup
delivery or extractable-inventory closure. Source-derived model rights remain
CC-BY-NC-3.0, separately from the software license.

## Required repository checks

```bash
python -m pytest -q tests/test_screen_wp6_lateral_identifiability.py tests/test_correction_i045.py tests/test_screen_i076.py
python -m pytest -q -m 'not slow and not live and not gpu and not external_data'
python -c 'from puckworks.registry import run_all_gates; run_all_gates()'
python -m ruff check puckworks/ tests/
python -m mypy
python -m puckworks.paper3.registry_artifacts --verify
python -m puckworks.paper3.build verify
python -m puckworks.paper3.availability --verify
python -m puckworks.paper3.corpus --verify
python -m puckworks.paper_a.claim_coverage
python -m puckworks.paper_b2.claim_coverage
python -m puckworks.paper3.claim_coverage
python -m puckworks.analysis.lateral_coupling_discrimination --verify
python -m puckworks.paper3.evidence_graph --reconcile
python -m puckworks.paper3.evidence_graph --verify
python -m puckworks.statusdoc --verify
git diff --check
```

The G0 repair-only baseline ran before scientific code was installed. It qualifies
the repair candidate, not unchanged remote main. Existing skips and the Taichi
zero-gate acknowledged exception remain explicit. No EWP native run or protected
scoring lane is part of generic QA. No successor or production adoption follows.
