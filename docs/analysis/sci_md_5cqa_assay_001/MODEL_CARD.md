# Research model card: first-assay 5CQA delivery

G1 / NO_GOVERNING_PHYSICS_CHANGE / RESEARCH_ONLY. [PROTOCOL.md](PROTOCOL.md)
fixes the four arms, source roles, exact mathematics, selection and acceptance.
A1 normalizes a fixed exponential by the original first-fraction interval-average
5CQA assay. L1 learns a five-knot logistic curve with exactly twenty coefficients
from FIT suffix outcomes, conditioned on m1, m2 and that same q1. E0/D0 are exact
historical controls and use their unchanged mass-only runtime and saved models.

Model, EarlyInput and State are immutable, strictly 5CQA-tagged objects with
hash-checked deterministic serialization. Inputs are named m1_kg, m2_kg,
q1_kg_kg (mg/g divided by 1000). No second assay, other analyte, TDS or recipe.
model.condition(early_input), state.predict_intervals(starts_kg,ends_kg), and
state.remaining_5cqa(stop_mass_kg) work from saved models without fitting, source
files or a network. Predictions carry kg/mg mass, mg/g interval concentration,
numerical allowances/qualification, hard support, extrapolation, model/training
identity, units, species and rights. Hard domain ends at 0.06971540000000001 kg;
forecast begins at m1+m2. remaining_5cqa is modeled delivery to the supplied stop,
not remaining puck inventory. Zero-width means are undefined.

FIRST_FRACTION_FIVE_CQA_ASSAY_REQUIRED. A1 assumes the fixed exponential extends
to [0,m1]; the old E0 model did not establish early-fraction validity. A1 has no
new fitted global parameter, while L1 need not reproduce the first interval.
Their difference does not isolate a physical shape mechanism. Extrapolated
features remain visible without clipping; numerical qualification does not prove
prediction accuracy. The study is SOURCE_INTERNAL, TARGET_EXPOSED and
RETROSPECTIVE_CAMPAIGN_SEPARATED_CONDITIONAL_PREDICTION, with no independent
validation, identified kinetics/inventory/batch effect, sensor-free control or
joint TDS closure. PHYSICAL_VALIDATION_NOT_ESTABLISHED.

Source-derived saved models/results retain Pannusch/Schmieder attribution and
CC-BY-NC-3.0 (Mendeley 10.17632/y2tz67f6ry.1), separately from software licensing.
