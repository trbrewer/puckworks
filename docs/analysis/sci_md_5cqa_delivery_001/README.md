# SCI-MD-5CQA-DELIVERY-001

Completed frozen comparison: **TESTED_FIVE_CQA_FAMILIES_INADEQUATE**.
Both E0 and D0 fail both adequacy limits in all four primary conditions.
Balanced RMSE is 0.364510463 versus 0.363520937 mg/g; D0 improves only
0.000989525 mg/g (0.2715%), with two condition wins. Only the bias-deterioration
increment passes. The saved-model research implementation is complete.

Read [RESULT.md](RESULT.md) and [RESULTS.json](RESULTS.json) for all arms,
conditions, allowances and original denominators. Support is FIT 177/180,
primary 48/48, temperature 24/24 and flow 23/24 windows. Three C08 shots
extrapolate m2; full-flow qualification is not established.

The separate [G0 repair](REPAIR.md) and [repair-only baseline](BASELINE.json)
precede scientific implementation. [QUALIFICATION.md](QUALIFICATION.md) reports
final QA and actual CI separately. The immutable protocol, development and
EXECUTION.json are pre-score snapshots; the latter correctly retains score=0.
Final score=1 is bound by [SCORE_COMPLETION.json](SCORE_COMPLETION.json).
[Independent approval](review.json) and [review report](INDEPENDENT_REVIEW.md)
bind the exact freeze. [HANDOFF.json](HANDOFF.json) contains compact identities.

G1 / NO_GOVERNING_PHYSICS_CHANGE; RESEARCH_ONLY; SOURCE_INTERNAL /
TARGET_EXPOSED / RETROSPECTIVE. No fresh validation, physical-validation or
mechanistic claim. Source-derived models/results remain CC-BY-NC-3.0,
Pannusch/Schmieder, Mendeley DOI 10.17632/y2tz67f6ry.1; originals and detailed
rows remain outside Git. No adoption, merge, EWP change or successor follows.

## Reproduction

The [saved-model API example and environment notes](COMMANDS.md) are executable
without a source workbook or prior-task private run. The private continuation
README records exact resolved local executables and paths.

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
