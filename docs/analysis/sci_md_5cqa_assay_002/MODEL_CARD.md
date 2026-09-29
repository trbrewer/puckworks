# Research model card: matched early-assay 5CQA delivery

SCI-MD-5CQA-ASSAY-002 / G1 / NO_GOVERNING_PHYSICS_CHANGE / RESEARCH_ONLY.
[PROTOCOL.md](PROTOCOL.md) fixes the mathematics, data roles and decisions.
L1M uses m1,m2,q1 (20 coefficients); L2M uses m1,m2,q2 (20); L12 uses
m1,m2,q1,q2 (25). Five equally spaced mass knots interpolate logits with
training-only centered features and fixed .01 SI scales. Coefficients [-20,20].
Separate chemical-column penalties preserve fixed-lambda nesting. No production
registration, kinetics, inventories or per-shot fit. Early assays are interval
averages used as covariates. All arms share the 42-shot eligible FIT cohort and
forecast anchor m1+m2. L2M requires m1 mass but no first chemical assay.

Immutable arm-specific input classes reject extra fields. Model.load(path),
model.condition(input), state.predict_intervals(starts_kg,ends_kg), and
state.remaining_5cqa(stop_mass_kg) need no source or optimizer. Inputs use kg and
kg/kg; named 5CQA mg/g converts by /1000. Results carry kg/mg analyte, mg/g
average, numerical allowance, hard support and feature-extrapolation flags.
Zero-width average is undefined. Hard domain is derived from FIT and cannot
exceed .06971540000000001 kg. Extrapolation is retained without clipping.

Remaining delivery is a model integral to the requested mass, not puck inventory
or measured whole-cup closure. Supplied mass is not hydraulic prediction.
SOURCE_INTERNAL / TARGET_EXPOSED /
RETROSPECTIVE_CAMPAIGN_SEPARATED_CONDITIONAL_PREDICTION.
Physical validation and analytical uncertainty remain NOT_ESTABLISHED.
No universal minimum-assay, joint TDS/composition or real-time HPLC-control claim.
Pannusch/Schmieder source-derived models/results retain CC-BY-NC-3.0,
Mendeley 10.17632/y2tz67f6ry.1, separately from software licensing.
