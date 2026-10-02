# Observed-boundary stopping replay

SCI-MD-MASS-STOP-DECISION-001, G1 / NO_GOVERNING_PHYSICS_CHANGE.
[Protocol](PROTOCOL.md) fixes the scientific question and every decision rule.
The task uses immutable MASS-007 early states and complete observed Grudeva
suffix boundaries; it does not add a model or authorize a controller.

Use an external private output directory and source/prior locators resolved
through the existing data-source configuration. From the isolated Puckworks
candidate, with one scientific worker and one BLAS thread:

```bash
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
python -m puckworks.analysis.grudeva_stopping_decision prepare \
  --prior "$PRIVATE_MASS007_RUN" --source-root "$PRIVATE_SOURCE_ROOT" \
  --out "$NEW_PRIVATE_RUN"
# Commit/test the candidate; freeze requires a clean committed tree.
python -m puckworks.analysis.grudeva_stopping_decision freeze --out "$NEW_PRIVATE_RUN"
# A fresh independent reviewer must approve this exact freeze before this command.
python -m puckworks.analysis.grudeva_stopping_decision_scoring \
  --out "$NEW_PRIVATE_RUN" --review "$PRIVATE_APPROVAL" \
  --source-root "$PRIVATE_SOURCE_ROOT"
```

These commands are a one-use scientific sequence. An existing output/start
receipt is never overwritten; do not replay a consumed score. Reports consume
retained scores only. Public results are aggregate; private originals, assay
rows, state/decision files and per-shot results must remain outside Git.

Run synthetic tests with `python -m pytest -q tests/test_grudeva_stopping_decision.py`.
Use maintained normal, scientific-baseline, registry, Ruff, mypy and generated/
evidence workflow checks for repository QA. No OpenFOAM or EWP write is needed.
No production adoption, merge, auto-merge or automatic successor is authorized.
PHYSICAL_VALIDATION=NOT_ESTABLISHED.
