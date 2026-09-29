# Reproduction: SCI-MD-5CQA-TDS-001

G1 / NO_GOVERNING_PHYSICS_CHANGE / RESEARCH_ONLY.
Use the committed producer and qualified Python environment. The original task
used Python 3.12.3, NumPy 2.5.3, SciPy 1.18.1 and the reconstruction extra
(openpyxl). Existing external configuration resolves the eight bound originals.
No originals, individual observations/predictions or detailed logs are in Git.
The retained private archive holds the resolved command transcript and paths.
Source-derived models and summaries: Pannusch/Schmieder, Mendeley
10.17632/y2tz67f6ry.1, CC-BY-NC-3.0; separate from software licensing.

The following records the authorized one-time stages. `RUN` is the original
private task run; `PARENT_006` is the existing retained 006 run, including all
fifteen excluded-design C2 parents. `REVIEW` is the actual independent approval
of that exact freeze. Do not create a fresh directory to reset the budget, rerun
scientific scoring, or refit an expired task. The durable task clock starts
2026-09-29T01:09:49Z and expires at 2026-09-29T07:09:49Z. Existing artifacts are
exclusive-write. Missing parents mean BLOCKED_DEPENDENCY, never permission to fit.

```bash
export OPENBLAS_NUM_THREADS=1
export OMP_NUM_THREADS=1
export MKL_NUM_THREADS=1
export PYTHONPATH=.
# Activate the qualified Python environment; resolve private archive paths.
python -m pytest -q \
  tests/test_conditional_5cqa_tds_delivery.py \
  tests/test_conditional_5cqa_tds_training.py \
  tests/test_pannusch_conditional_5cqa_tds_delivery.py
python -m puckworks.analysis.pannusch_conditional_5cqa_tds_delivery \
  prepare --out "$RUN" --parent-evidence "$PARENT_006"
python -m puckworks.analysis.pannusch_conditional_5cqa_tds_delivery \
  develop --out "$RUN"
python -m puckworks.analysis.pannusch_conditional_5cqa_tds_delivery \
  freeze --out "$RUN"
# Genuine independent exact-freeze approval is required before score.
python -m puckworks.analysis.pannusch_conditional_5cqa_tds_delivery \
  score --out "$RUN" --review "$REVIEW"
python -m puckworks.analysis.pannusch_conditional_5cqa_tds_delivery \
  verify --out "$RUN"
python -m puckworks.analysis.pannusch_conditional_5cqa_tds_delivery \
  report --out "$RUN"
```

`verify` checks frozen identities and saved inference only, with zero fitting,
source-workbook reads, outcome joins or rescoring. `report` reads and verifies
retained scores only. For archival replay, restore the exact frozen scientific
files and their unchanged predecessors; reporting additions do not replace the
producer identity. External originals are required by prepare/score, not by the
saved-model runtime. The runtime loads its hash-verified sibling numerical
primitives and embedded C2; it has no installed-package fallback.

A runnable saved-model API example uses invented inputs and a synthetic model:

```bash
PYTHONPATH=. python docs/analysis/sci_md_5cqa_tds_001/synthetic_saved_model_example.py
```

It saves/loads an S2 model, round-trips an immutable conditioned state and calls
`remaining_5cqa(.06)`. It is **SYNTHETIC_ONLY_NOT_A_PHYSICAL_SHOT**. Its remaining
integral is modeled delivery after the first two fractions, not inventory or a
measurement of the intervening unassayed beverage. Production defaults and EWP
remain unchanged.
