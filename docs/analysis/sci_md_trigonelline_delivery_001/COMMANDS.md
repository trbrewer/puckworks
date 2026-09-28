# Retained execution and reproduction

SCI-MD-TRIGONELLINE-DELIVERY-001; RESEARCH_ONLY;
NO_GOVERNING_PHYSICS_CHANGE. Resolve PW, EWP, OUT and REVIEW from the
private location record and configured source resolver. OUT is outside both
repositories. Source originals and row-level evidence are not distributed.
The portable identities and supported environment versions are in BASELINE.json,
DEPENDENCIES.json, SOURCE_IDENTITIES.json and QUALIFICATION.json.

The commands below document the completed experiment. `prepare`, `develop`,
`fit`, `predict`, `freeze` and `score` are mutation commands, not reproduction
commands. They must not be repeated on this retained campaign. Their exclusive
receipts preserve failures and prevent a second score. No historical scientific
CLI was replayed. The required routine suites include existing historical
result-reproduction tests.

## Original execution

From the clean task checkout and the existing source-capable Python environment:

```bash
export PYTHONPATH=.
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
python -m pytest -q -ra \
  tests/test_conditional_trigonelline_delivery.py \
  tests/test_conditional_trigonelline_training.py \
  tests/test_pannusch_conditional_trigonelline_delivery.py
python -m puckworks.analysis.pannusch_conditional_trigonelline_delivery prepare --out "$OUT"
python -m puckworks.analysis.pannusch_conditional_trigonelline_delivery develop --out "$OUT"
python -m puckworks.analysis.pannusch_conditional_trigonelline_delivery fit --out "$OUT"
python -m puckworks.analysis.pannusch_conditional_trigonelline_delivery predict --out "$OUT"
python -m puckworks.analysis.pannusch_conditional_trigonelline_delivery freeze --out "$OUT"
```

The independent reviewer inspects the exact frozen head/tree and evidence.
Only its genuine APPROVED receipt permits the single original scoring command:

```bash
python -m puckworks.analysis.pannusch_conditional_trigonelline_delivery score --out "$OUT" --review "$REVIEW"
```

No outcomes may enter development, preprocessing, selection, support or
prediction. Synthetic verification values never enter campaign counts/scores.

## Read-only reproduction

Use a clean checkout containing the frozen science, the recorded environment,
and read-only retained evidence. These commands do not fit, join outcomes or
create another score. `report` reads the existing score and its completion
receipt; it does not recompute the scientific comparison.

```bash
export PYTHONPATH=.
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
python -m puckworks.analysis.pannusch_conditional_trigonelline_delivery verify --out "$OUT"
python -m puckworks.analysis.pannusch_conditional_trigonelline_delivery report --out "$OUT"
```

`verify` binds the 53 scientific code/protocol files to the exact reviewed
commit/tree, checks all 646 pre-score artifacts and source registers, and
requires byte-identical canonical predictions/states for every saved slot.
The reviewed identity remains distinct from later reporting/publication commits.
The public models support direct mass-coordinate inference without an optimizer;
row-level reproduction additionally requires authorized private evidence access.

## Regression and repository checks

From a clean Puckworks checkout in the recorded routine environment:

```bash
export PYTHONPATH=.
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
python -m pytest -q -ra
python -c "from puckworks.registry import run_all_gates; run_all_gates()"
git diff --check
ruff check --output-format=github puckworks/ tests/
mypy
```

From the unchanged EWP checkout in its existing pinned environment and recorded
optional source-authority configuration:

```bash
python3 -m unittest discover -s tests -p 'test_*.py'
git diff --exit-code
```

Current applicable workflow commands, actual outcomes, log hashes, skips,
xfails and any unavailable platform/environment checks are retained in
QUALIFICATION.json. All pre-existing tests, assertions, tolerances, skips,
xfails and workflows are unchanged. Source/static/historical/change-declaration,
shell/JSON, boundary and secret/path checks are included. No Allrun, Allverify
or native OpenFOAM launch is part of this task.
