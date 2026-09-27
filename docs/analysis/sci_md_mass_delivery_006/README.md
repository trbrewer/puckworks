# Learned early-to-late delivery

G1 / NO_GOVERNING_PHYSICS_CHANGE. [Issue #287](https://github.com/trbrewer/puckworks/issues/287),
[EWP issue #193](https://github.com/trbrewer/espresso-whole-pull/issues/193).
[Model card](MODEL_CARD.md), [protocol](PROTOCOL.md),
[source preflight](DATA_AVAILABILITY_PREFLIGHT.json),
[pre-freeze numerical correction](NUMERICAL_ADDENDUM.md).

C2 CONDITIONAL_TAIL_SPLINE is the fixed primary. C0 MASS_CONTEXT_TAIL_SPLINE
and C1 FIRST_ASSAY_TAIL_SPLINE test the added early-assay information. All use
the same five-knot domain/basis and train on suffix interval-average TDS from
all 45 FIT shots. Fractions 1/2 condition; 3/5/7/10 are supervised responses.
The former 30-shot FIT-transfer population is training for 006 only. PRED
suffix chemistry is attached only after independent exact-freeze approval.
005's fixed amplitude/rate-family rejection is preserved.

Use an existing environment with repository-supported NumPy/SciPy/openpyxl.
No installation or dependency upgrade is required by these commands. Private
output must be new and outside Git; source locators use existing configuration.
`LEGACY_PREDICTIONS` points to retained 005 predictions whose accepted hash is
verified automatically. Never point it at a historical scorer.

```bash
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
export PYTHONPATH=.
python -m puckworks.analysis.conditional_tail_delivery --synthetic --arm C2
python -m puckworks.analysis.conditional_tail_delivery --synthetic --save-model "$SYNTHETIC_MODEL"
python -m puckworks.analysis.conditional_tail_delivery --synthetic --load-model "$SYNTHETIC_MODEL"
python -m puckworks.analysis.pannusch_conditional_tail_delivery prepare --out "$PRIVATE_RUN"
python -m puckworks.analysis.pannusch_conditional_tail_delivery develop --out "$PRIVATE_RUN"
python -m puckworks.analysis.pannusch_conditional_tail_delivery fit --out "$PRIVATE_RUN"
python -m puckworks.analysis.pannusch_conditional_tail_delivery predict --out "$PRIVATE_RUN" \
  --retained-legacy "$LEGACY_PREDICTIONS"
# Commit implementation/public model artifacts before freezing.
python -m puckworks.analysis.pannusch_conditional_tail_delivery freeze --out "$PRIVATE_RUN"
# Only after a fresh independent reviewer approves this exact freeze:
python -m puckworks.analysis.pannusch_conditional_tail_delivery score --out "$PRIVATE_RUN" --review "$REVIEW"
# Reporting only reads verified retained score artifacts; no fitting or scoring:
python -m puckworks.analysis.pannusch_conditional_tail_delivery report --out "$PRIVATE_RUN"
python -m pytest -q tests/test_conditional_tail_delivery.py tests/test_conditional_tail_training.py \
  tests/test_pannusch_conditional_tail_delivery.py
```

The public API is `Model.load(path)`, `model.condition(EarlyInput(...))`,
`predict_intervals(state, starts_kg, ends_kg)` and
`remaining_solute(state, stop_mass_kg)`. Strict model/state serialization binds
schema, units, features and derived contents. C0 accepts exactly masses; C1 adds
q1; C2 adds q2. Query windows are independent, so later windows cannot alter an
earlier answer. Early concentrations are kg/kg; output TDS is percent by mass.
Queries before the anchor, beyond the training domain or with unknown/nonfinite
coordinates fail. Zero width gives zero solute and undefined average TDS.

`DEVELOPMENT.json` contains all 12 lambda diagnostics and every fold's support.
These are selected-hyperparameter development diagnostics, not unbiased nested
validation or another transfer panel. `SOURCE_COUNTS.json` records the actual
eligible roles and support. `EXECUTION.json` records bounded real computation;
all start logs, source observations and row predictions are retained privately.
Coefficient artifacts in `models/` are source-derived CC-BY-NC-3.0 research
artifacts, separate from first-party software licensing. Pannusch/Schmieder,
Mendeley 10.17632/y2tz67f6ry.1. The frozen legacy empirical reference keeps its
exact older domain/runtime; same-training-data comparisons are C2 versus C0/C1.

RESEARCH_ONLY / SOURCE_INTERNAL / TARGET_EXPOSED /
RETROSPECTIVE_CAMPAIGN_SEPARATED_CONDITIONAL_PREDICTION.
Separation prevents further leakage but cannot undo earlier campaign exposure.
No fresh blind holdout, independent validation, identified physical mechanism,
universal coffee behavior or measured whole-cup/inventory closure is claimed.
Supplying beverage mass does not predict hydraulics; modeled gaps are not measured
solute. Feature extrapolation flags establish no evidence of accuracy.
PHYSICAL_VALIDATION=NOT_ESTABLISHED; NATIVE_EWP_RUNS=0.
MERGE_AUTHORIZED=false; PRODUCTION_ADOPTION_AUTHORIZED=false;
NO_SUCCESSOR_AUTHORIZED. No laboratory operation or new acquisition.
