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

The separate fresh final-review session found the full-recovery audit scaling
counterexample, then reviewed the necessary log-domain repair before scoring.
It supplied tiny-informative-calibration, noisy-cancellation and tiny-pulse
counterexamples, all added as regression tests. It independently ran the 33
synthetic tests (all passed; release-surface test excluded from that run).
Fast sparse versus forced row-log-sum-exp prediction difference was <=1.78e-15,
objective-gradient difference <=1.03e-15; finite-difference gradient discrepancy
<=1.38e-9. Full-recovery independent audit error on its ordinary examples was
<=4.14e-14. It found no remaining concrete restart blocker, conditional on baseline
replay, actual selected-model audits and final aggregate/claim review. Numeric
range limits and all failed runs must remain disclosed.

After the actual GL16 gate failure, the fresh reviewer verified the pressure-span
subdivision repair: **37 synthetic tests passed** (release-artifact test omitted).
Independent nonuniform-time A/AR integrals agreed within 4.58e-16; finite-difference
gradient discrepancy was <=1.65e-10. It verified that saved integration settings
actually control prediction: a synthetic early-4-bar/later-0-to-15-bar example
changed from 1.8917447883 with legacy GL16 to 1.896148931654 with refinement,
against independent reference 1.896148931646. The sharp n=1000 regression still
fails the numerical gate. No concrete restart blocker remained, subject to
baseline replay, actual audits and final aggregate claims review.

The final reviewer also checked complete-shot audit batching after the recorded
large-array indexing exception. It independently ran 39 synthetic tests, verified
identical results across five batch boundaries for passing and failing full-R
examples, and confirmed that ownership corruption is rejected before indexing.
No concrete mathematical or calibration defect was found. Root cause of the
execution host's indexing failures remains unresolved. Actual audits and all
selected-fit replays are required before the final claims review.

## Final independent review — cleared

The fresh final-review session carried forward its observation/window/calibration,
fold isolation, baseline fairness, nesting and mathematical review, then checked
the actual public models, numerical receipts, aggregate tables, figures and claims.
It independently ran the final **41 focused tests: all passed**. No raw private
records or identifiers were inspected, and it did not independently rescore shots.

It verified all 48 model/audit hashes; all 42 selected optimizer-success statuses;
the 12 nested training-objective comparisons; all 384 score rows' fold-user
aggregation (maximum discrepancy 2.27e-13); all 24 paired contrasts against model
mean differences (maximum discrepancy 7.78e-14); release minimum cells; and the
55.8580940841 recorded core-hour accounting sum. Actual quadrature/replay outcomes
were assessed through their qualified receipts. Code hashes and the unchanged
scored-aggregate hashes in SCORING_RECEIPT.json match.

Concrete final fixes: suppress actual contributor-user transitions separately
from changing-shot support; skip empty panel bins; break figure lines over
suppressed bins; show markers for isolated released predictions; label the
negative-increment diagnostic as native increments. These publication corrections
use the original cached predictions and do not alter any scored aggregate,
model, corpus, fold or scoring setting. Failed display artifacts remain private.

The reviewer found no remaining concrete defect. It confirmed that SUMMARY and
RESULTS distinguish T0's primary win from the normalized ranking, acknowledge
large heterogeneous errors, separate reconstruction/deployment from prediction,
and retain the empirical claim ceiling and unresolved execution limitations.
Required repository and hosted CI are separate checks, not part of this verdict.
