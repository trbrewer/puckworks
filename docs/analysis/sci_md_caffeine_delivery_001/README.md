# Caffeine interval delivery

SCI-MD-CAFFEINE-DELIVERY-001; [Puckworks #289](https://github.com/trbrewer/puckworks/issues/289),
[EWP #195](https://github.com/trbrewer/espresso-whole-pull/issues/195).
G1 / NO_GOVERNING_PHYSICS_CHANGE. [Model card](MODEL_CARD.md), [protocol](PROTOCOL.md),
[source preflight](DATA_AVAILABILITY_PREFLIGHT.json), [dependency identities](DEPENDENCIES.json).

Fixed arms D0 (no TDS), S0 (constant C2 share), S1 (mass-context share) and primary
S2 (early-TDS-conditioned share). Only later caffeine fractions 3/5/7/10 supervise
heads. Fraction-1/2 masses and TDS condition share inference; no query-time
caffeine assay. S1 already uses early TDS indirectly through frozen C2.

Use an existing NumPy/SciPy/openpyxl environment. Private paths below are supplied
through local configuration, never committed. PARENT_006_EVIDENCE denotes the
retained 006 run with its accepted freeze and 15 C2 .0001 fold artifacts.
No parent refitting, historical scorer or dependency installation is required.

```bash
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
export PYTHONPATH=.
python -m pytest -q tests/test_conditional_caffeine_delivery.py \
  tests/test_conditional_caffeine_training.py tests/test_pannusch_conditional_caffeine_delivery.py
python -m puckworks.analysis.pannusch_conditional_caffeine_delivery prepare \
  --out "$PRIVATE_RUN" --parent-evidence "$PARENT_006_EVIDENCE"
python -m puckworks.analysis.pannusch_conditional_caffeine_delivery develop --out "$PRIVATE_RUN"
python -m puckworks.analysis.pannusch_conditional_caffeine_delivery fit --out "$PRIVATE_RUN"
python -m puckworks.analysis.pannusch_conditional_caffeine_delivery predict --out "$PRIVATE_RUN"
# Commit implementation and attributed public models before freezing.
python -m puckworks.analysis.pannusch_conditional_caffeine_delivery freeze --out "$PRIVATE_RUN"
# Only genuine independent approval of this exact freeze permits the next command.
python -m puckworks.analysis.pannusch_conditional_caffeine_delivery score --out "$PRIVATE_RUN" --review "$REVIEW"
python -m puckworks.analysis.pannusch_conditional_caffeine_delivery report --out "$PRIVATE_RUN"
```

Public API, without source workbooks, targets or optimizer:

```python
from puckworks.analysis.conditional_caffeine_delivery import Model, EarlyInput
model = Model.load("docs/analysis/sci_md_caffeine_delivery_001/models/S2.json")
state = model.condition(EarlyInput("S2", (0.004, 0.004, 0.15, 0.10), "SYNTHETIC"))
intervals = state.predict_intervals([0.008, 0.02], [0.02, 0.04])
remaining = state.remaining_caffeine(0.04)
```

The example values are synthetic. Output gives kg caffeine, mg, mg/g, geometry,
quadrature differences/allowance, support and feature-extrapolation flags. S0/S1/S2
embed unchanged parent C2 coefficients and import its exact verified runtime.
D0 accepts only m1/m2 and embeds no parent state. Remaining caffeine over unassayed
gaps is modeled, not measured whole-suffix or whole-cup validation. Zero widths
have zero mass and undefined concentration. Numerical allowance is not confidence.

RESEARCH_ONLY / SOURCE_INTERNAL / TARGET_EXPOSED /
RETROSPECTIVE_CAMPAIGN_SEPARATED_CONDITIONAL_PREDICTION.
Analytical recovery/censoring uncertainty remains unestablished. Source-derived
models retain Pannusch/Schmieder, Mendeley 10.17632/y2tz67f6ry.1, CC-BY-NC-3.0
attribution separately from software licensing. Caffeine is already part of TDS.
PHYSICAL_VALIDATION=NOT_ESTABLISHED; MERGE_AUTHORIZED=false;
PRODUCTION_ADOPTION_AUTHORIZED=false; NATIVE_EWP_RUNS=0; NO_SUCCESSOR_AUTHORIZED.
