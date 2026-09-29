# Execution and retained replay

SCI-MD-5CQA-ASSAY-001 / G1 / NO_GOVERNING_PHYSICS_CHANGE / RESEARCH_ONLY.
The single authorized execution uses Python 3.12.3, NumPy 2.5.3, SciPy 1.18.1
and openpyxl for source projection. No dependency lock or registry is changed.
Use the existing registered corpus resolver; no acquisition is required.

Resolve the actual private paths from the existing source configuration:

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
TASK_EVIDENCE_ROOT="$SOURCE_ROOT/5cqa-assay-001-evidence-20260929T122232Z"
EVIDENCE_ROOT="$TASK_EVIDENCE_ROOT/run-001"
REVIEW_RECEIPT="$TASK_EVIDENCE_ROOT/review/review.json"
RUNNER=puckworks.analysis.pannusch_assay_conditioned_5cqa_delivery
```

The private task README records the exact local interpreters and paths. The
first four commands record this one execution; they are not casual rerun commands.
Exclusive starts and immutable receipts prohibit resets or a second outcome join.
The independent reviewer supplies the exact-freeze receipt; implementation does
not supply its own approval. The fixed deadline is this task's fresh clock.

```bash
python -m "$RUNNER" prepare --out "$EVIDENCE_ROOT"
python -m "$RUNNER" develop --out "$EVIDENCE_ROOT"
python -m "$RUNNER" freeze --out "$EVIDENCE_ROOT"
python -m "$RUNNER" score --out "$EVIDENCE_ROOT" --review "$REVIEW_RECEIPT"
python -m "$RUNNER" verify --out "$EVIDENCE_ROOT"
python -m "$RUNNER" report --out "$EVIDENCE_ROOT"
```

Only verify/report are repeatable: verify checks the bound files and replays saved
inference; report reads hash-bound retained results. Neither fits, joins outcomes
or rescores. No predecessor scoring entry point is invoked.

For source-free inference, from the repository root:

```bash
python docs/analysis/sci_md_5cqa_assay_001/synthetic_saved_model_example.py
```

The example loads published A1/L1 models and uses illustrative masses and a first
assay. It needs no corpus, private evidence, fitting module or network. Inputs
are kg and kg/kg; exactly 5CQA mg/g converts by division by 1000. Queries start at
m1+m2 and end at or below 0.06971540000000001 kg. Always inspect numerical
qualification and feature extrapolation. Modeled remaining delivery is not puck
inventory or measured whole-cup closure. Source-derived models/results retain
Pannusch/Schmieder CC-BY-NC-3.0 attribution, separately from software licensing.

Required QA uses the normal pytest selector, registry gates, ruff, mypy,
statusdoc, generated registry/build/availability/corpus checks, paper claim checks,
lateral-coupling verification, evidence-graph verification and strict reconciliation,
scientific_baseline, data-guide and README governance verification, and git diff
--check. BASELINE.json records the unchanged base; final QA records the tested
candidate, commands and outcomes. Generic QA never invokes protected scoring.
