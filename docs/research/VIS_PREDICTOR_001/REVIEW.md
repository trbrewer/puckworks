# Review record

A fresh independent read-only pre-scoring session reviewed the observation,
onset/window/guard rules, mass/time coordinates, grouped folds, direct amplitude,
objective and derivatives, nesting, baseline fairness and release code. It did not
inspect private flow values, fit models, score held-out data or modify files.

Concrete corrections before the freeze:

- Scale calibration bases per shot in the batch solve and reusable predictor,
  preventing squared tiny bases from becoming an arbitrary zero amplitude.
- Suppress the complete fold partition within each reported subset when a fold
  or complement is too small; do not allow subtraction from an overall total.
- Protect entrants and departures separately between aggregate-panel support sets.
- Distinguish generic supplied-flow presence from absence. Weight provenance remains
  unknown; no known-estimated-weight cohort is established by the retained authority.
- Replace provisional four-point pressure quadrature with sixteen-point quadrature
  and a covariate-only selected-model adequacy gate before any scoring. Synthetic
  sharp-shape examples demonstrate why the gate is needed. The provisional private
  preparation is retained separately; it never produced a fit or held-out score.

The reviewer verified bitwise kappa=0 nesting and seven analytic gradients against
finite differences (maximum discrepancy 3.1e-11 on its synthetic examples).
The corrected focused suite has 25 passing tests before freezing. The required
final fresh read-only review will be recorded here after results exist.

The same read-only reviewer verified all corrections and independently reran
the final 25-test focused suite (25 passed). It found no remaining pre-scoring
blocker, conditional on the committed freeze and actual quadrature gate passing.
The raw returned amplitude's representability limit is documented; prediction
multiplication stays normalized. These changes precede any fit or score.

Before freezing, exact-value pressure-node deduplication replaced repeated capacity
function evaluation with a sparse weighted window operator (no bins or rounding).
The reviewer confirmed numerical equivalence and the native-endpoint pressure-range
reconstruction, and independently reran the expanded suite: **26 passed**. The
final recommendation rule includes all eight declared models on the primary metric,
with M0/A still labelled sensitivities. No new pre-scoring defect was found.
