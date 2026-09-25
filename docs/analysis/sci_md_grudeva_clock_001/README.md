# Grudeva time versus beverage-mass research predictor

Bounded retrospective source-conditioned whole-shot-grouped evaluation.
Read [PROTOCOL.md](PROTOCOL.md) for source interpretation, fitting and decisions.
No registered model or production integration. Upstream author: Dr. Yoana Grudeva,
[espresso-model](https://github.com/YoanaGrudeva/espresso-model/tree/567ad8f3808eb74fbe3e470eaa333161bf2eac1c),
[thesis](https://pure.port.ac.uk/ws/portalfiles/portal/88405472/Final_Thesis_Yoana_Grudeva.pdf).

From this checkout with numpy/scipy installed (matplotlib only for report), use a
permission-consistent source file and a NEW private output directory outside Git:

```bash
export PRIVATE=/path/to/private/task
python -m puckworks.analysis.grudeva_clock audit --source "$PRIVATE/source/exp13.csv" --out "$PRIVATE/audit"
python -m pytest -q tests/test_grudeva_clock.py
# Only after independent APPROVED_FOR_SCORING against the exact freeze:
python -m puckworks.analysis.grudeva_clock fit-predict --source "$PRIVATE/source/exp13.csv" --freeze docs/analysis/sci_md_grudeva_clock_001/FREEZE.json --review docs/analysis/sci_md_grudeva_clock_001/review/PRE_SCORING.json --out "$PRIVATE/predictions"
python -m puckworks.analysis.grudeva_clock score --source "$PRIVATE/source/exp13.csv" --bundle "$PRIVATE/predictions" --out "$PRIVATE/scored"
python -m puckworks.analysis.grudeva_clock report --source "$PRIVATE/source/exp13.csv" --bundle "$PRIVATE/predictions" --scores "$PRIVATE/scored" --out "$PRIVATE/report"
```

Source discovery: explicit `--source` is the first-priority path under the existing
external-data rules. The configured inventory root was checked; it contained only
the three historical summary/provenance/parameter files, not the raw CSV/notebook.
The specifically authorized public upstream files were retrieved at a pinned
commit into private storage. The notebook was read as JSON, never executed.
No source file is inferred absent merely because it is not committed.

The public tests use only synthetic observations. Reproducing real-data results
requires the permissioned source; row-level outputs and plots must remain private.
Aggregate publication does not add the raw per-shot data to repository scope.
