# Reproduce the bounded empirical transfer evaluation

G1 / NO_GOVERNING_PHYSICS_CHANGE. [Protocol](PROTOCOL.md) fixes the primary
ANCHORED_EMPIRICAL, ten conditions, five arms and axes A–E. [Qualification
card](QUALIFICATION_CARD.md) limits research use. Issue [#283](https://github.com/trbrewer/puckworks/issues/283),
linked EWP [#189](https://github.com/trbrewer/espresso-whole-pull/issues/189).

Use a checkout of the evaluation commit in FREEZE.json and a Python environment
with NumPy, SciPy and the existing reconstruction extra (openpyxl). Resolve the
original corpus using PUCKWORKS_EXTERNAL_DATA_ROOT or the configured Puckworks
source location. A missing source is reported; no alternative dataset is sought.
Set RUN to a new task-specific external directory and REVIEW to the independent
reviewer's receipt. Never point RUN inside any public Git checkout.

```bash
python3 -m puckworks.analysis.pannusch_empirical_transfer prepare --out "$RUN"
python3 -m puckworks.analysis.pannusch_empirical_transfer freeze --out "$RUN"
# Independent exact-freeze review must approve before the following command.
python3 -m puckworks.analysis.pannusch_empirical_transfer score --out "$RUN" --review "$REVIEW"
python3 -m puckworks.analysis.pannusch_empirical_transfer report --out "$RUN"
```

The contract was committed before extracting anchors. Preparation writes minimal
anchors, coordinate-only queries and 750 predictions/status records externally.
Freeze requires a clean committed implementation; existing/frozen/scored outputs
refuse overwrite. Score verifies the existing independent receipt, code, model,
source, support, coordinate and prediction hashes. An exclusive score receipt
preserves attempted execution and blocks a second score, including failed attempts.
Report only reads aggregates; it never reattaches chemistry or scores again.
The implementation author must not fill in their own independent approval.

The executed frozen scorer has a known classification defect: it suppresses
condition failure when support is incomplete, even when complete-shot error
contributions already prove failure with the original three-shot denominator.
Its `report` command faithfully returns the original raw aggregates. Read
[ADJUDICATION.json](ADJUDICATION.json) and [RESULT.md](RESULT.md) for the separately
reviewed material correction: A/D FAIL; B/C/E incomplete-support. No predictions,
scores, metric values or thresholds were changed and no score was repeated.
The unchanged frozen protocol's complete-condition restriction is an explicit
erratum, not authority to hide a definite failure. Prior result/review versions
are retained in commit 135bdc87d3e57f32743194d39c3f85940c5157d2.

```bash
PYTHONPATH=. python3 -m pytest -q tests/test_pannusch_empirical_transfer.py \
  tests/test_anchored_mass_delivery.py tests/test_mass_delivery.py \
  tests/test_conditioned_mass_delivery.py
python3 -m ruff check puckworks/analysis/pannusch_empirical_transfer.py \
  tests/test_pannusch_empirical_transfer.py
```

These offline tests use synthetic observations. The source-independent frozen
artifacts are checked by hash. No ordinary CI dependency on private workbooks.
Raw files, real anchor states, row predictions, per-shot metrics and execution
logs stay outside Git. Public aggregates retain Pannusch/Schmieder attribution,
CC-BY-NC-3.0, DOI 10.17632/y2tz67f6ry.1, separately from software licensing.
No physical validation, production adoption, native execution, merge or successor.
