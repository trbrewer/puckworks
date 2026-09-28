# Research model card: 5CQA interval delivery

Exactly two models, E0 and D0, defined in [PROTOCOL.md](PROTOCOL.md). Species
identity is strictly `5CQA`. They are research predictors; neither is registered
as a production component or selected default. NO_GOVERNING_PHYSICS_CHANGE.

E0 has two global bounded parameters A and L and an analytic exponential
integral. D0 has fifteen bounded coefficients and the accepted five-knot
mass-conditioned logistic spline architecture. D0 coefficients are trained
only on original 5CQA FIT interval observations. Neither model imports any
predecessor fitted coefficient, TDS curve, inventory or chemical input.

`Model.load(path).condition(EarlyInput(arm, (m1_kg,m2_kg)))` creates immutable
mass-only state. `predict_intervals(starts_kg,ends_kg)` returns integrated
5-CQA kg/mg and interval average mg/g, numerical allowances, source/model
identity and support/extrapolation status. `remaining_5cqa(stop_mass_kg)`
integrates from m1+m2. Runtime requires only saved public model files and the
numerical code; no training, workbook or predecessor private run is required.
The hard domain is training-derived and cannot be extended. Feature range
extrapolation is diagnostic. Zero-width concentration is undefined.

Qualification is conditional on measured beverage mass in the named retrospective,
source-internal, target-exposed campaign. Predictions across unassayed gaps are
modeled outputs, not measured whole-cup or inventory closure. There is no
identified kinetics/species transport, universal coffee transfer or physical
validation claim. Numerical allowances are not assay uncertainty.

Source-derived fitted models and aggregate results retain CC-BY-NC-3.0:
Pannusch/Schmieder, Mendeley DOI 10.17632/y2tz67f6ry.1. Software licensing does
not change those terms. Source binaries and detailed rows remain external.
