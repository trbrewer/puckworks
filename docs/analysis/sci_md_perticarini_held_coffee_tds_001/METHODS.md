# SCI-MD-PERTICARINI-HELD-COFFEE-TDS-001

G1 / NO_GOVERNING_PHYSICS_CHANGE / RESEARCH_ONLY. This is a conditional
reported-condition observer comparison, with private numerical results.
The owner-specified family, memberships and policy are frozen before fitting.
One implementation/review cycle; at most one material pre-score correction.
No prior decision, NONSCORING classification, production default or gate changes.

## Authority and inspection

Base PR384 `08e02ccc1a7da6e2a323678ccdba60f3181e6f94`, parent PR383
`6a97530d746269cf9e9d46dbcbdfd83e54a2caf5`; main
`21669a427145194e1f4003e3cf1b97dedefe2679`; read-only EWP
`f44c33dbb9b4fb80143e360e6f4a90f8ac0aa516`.
Chemical operator producer PR368 `fab67de4e82f3b76352df794056a53d70f32029d`;
duration producer PR360 `7bc013d4e00e416fb747d4c37e3cc514dc2e098d`.
Their exact operator, SOURCE_NOTES, RESULT and observation-view bytes are checked
against those Git identities. Accepted pure `load_observations` is reused;
old compute/write/figure campaigns are never invoked.

| Canonical input | SHA256 | Git blob |
|---|---|---|
| perticarini2024/ey_tds_cibao.csv | 2c5fae8319d41c690b7e23ea00ddfc722e08c01ebcd8f012dafb1820a8fc6703 | 0c657a30b7c8e048459e79a0b6e34980cba26f75 |
| egidi2024/table2_egidi2024_tds_ey.csv | 1b5cd8891472d2d432fcb96a59e167d8fcca8b8e70a0a75187d810bf8a8e4419 | 2f83cd9b59349cd2cf0e9b085ccf5ac03263cff5 |

Headers, source labels, complete dataset/coffee/temperature/pressure/grind keys,
all numeric fields and exact decimal spellings/order are reconstructed against
the accepted 30-row chemical observation view. Tables 4.3 and Egidi Table 2
are the SAME Modœtia observations, counted once. Original PDFs and raw shot
records are not reopened. Existing intake receipts authenticated the original
Tables 4.2/4.3 and Table 2; this task authenticates retained numerical authority.
Relevant source cards, provenance, available-data guide/register, manifest and
prior result/operator notes are inspected. Inspection scope and hashes are private.
No Wadsworth/trigonelline numerical bundle is an input; no new acquisition.

Attribution: A. Perticarini, *Predictive Models in Espresso Coffee Percolation*
(University of Camerino thesis, 2024); N. Egidi, J. Giacomini, E. Larsson and
A. Perticarini, *An improved numerical scheme for coffee Extraction Yield
evaluation*, Chaos, Solitons and Fractals 188 (2024), 115625,
DOI 10.1016/j.chaos.2024.115625. Existing factual-table rights notices apply;
no blanket source licence, PDF or source-artwork redistribution is implied.

## Observation and information basis

All 30 condition means: Cibao18, including both12-bar extreme-grind rows;
Modœtia12. Source-reported chemical extractions54+36 are underlying counts,
not authenticated shot membership. Zero individual-shot records; no expansion
to90 observations. Reciprocal folds Cibao18→Modœtia12 and Modœtia12→Cibao18;
120 held-coffee point predictions. Equal source-condition weights at point.

Both tables: SOURCE_INTERNAL / TARGET_EXPOSED / RETROSPECTIVE. Previously
inspected means and summaries remain exposure. D3 additionally conditions on
reported condition duration, available after extraction. R3/T2 use nominal
machine settings; N no recipe predictor. Matching coefficient counts does not
match information timing. Native grinds define within-coffee blocks only.
Duration's statistic, replication, clock, rounding and uncertainty are unknown;
not authenticated mean shot time, residence or contact time. Nominal pressure
and temperature are not measured puck histories. No cross-grinder mapping.

Response is direct reported refractometer TDS on its percentage scale; all
errors are TDS percentage points (pp). Nominal refractometer-equivalent beverage
mass-fraction convention, without independently calibrated gravimetric accuracy.
No density conversion. Three prepared beverage extractions/configuration:
C_bar=mean(C_j), EY_bar=mean(C_j/r_j), r_j=dose_j/beverage_mass_j.
EY and TDS SD remain provenance only. No exact masses/ratio from means, inverse-SD
weights, SD/sqrt(3), Gaussian noise, flow40/tau, pooled Table4.1 times or model flux.
Printed zero SD is not an exact mean. Earlier deterministic boxes are not noise
models and their historical contrast results are not replayed.

## Frozen model and numerical policy

xD=ln(tau_s/30), xR=ln(nominal_pressure_bar/9), xT=(temperature_degC−91.9)/1.5.
Original-scale predictions: D3=d0+dD*xD+dT*xT; R3=r0+rR*xR+rT*xT;
T2=t0+tT*xT; N=n0. Coefficient counts3/3/2/1. Independent unrestricted weighted
least squares, same responses/weights for every arm; N analytic weighted mean.
No shared coefficients, target response fit, tuning, ridge, clipping, bounds,
extra interactions/transforms or grind/EY/SD/coffee-offset predictors.
The logarithms are fixed empirical features, not kinetic or pressure laws.

Float64; finite positive duration/pressure, finite temperature/TDS; finite
nonnegative weights with positive total. Positive-weight source rows alone set
weighted centers and population SDs. Zero-weight records retain predictions.
Full-rank SVD; threshold eps*max(active weighted matrix shape)*largest singular
value. Independent QR and explicit inverse coefficient map must agree in
predictions within1e-9*max(1,abs(yhat))pp. All coefficients, transforms, ranks,
singular values, conditioning, SSE and discrepancies are saved per fit/source.
N is independently checked by QR. No pseudoinverse fallback or dropped terms.
Nested SSE checks D3≤T2≤N and R3≤T2≤N allow1e-12*max(1,comparator SSE).
All finite extrapolations and predictions outside0–100% are retained and flagged.
Source marginal ranges and target flags are saved; marginal containment is not
joint support. Near-degenerate duration supports can yield unstable slopes;
this is reported without rescue. No GSA deliverable or physical identification.

## Exact paired block enumeration

Fixed strata: Cibao core {fine,optimal,coarse},3 draws from3; Cibao extremes
{extra_fine,extra_coarse},2 from2; Modœtia {fine,optimal,coarse},3 from3.
Each block carries all original pressures and temperatures. Enumerate all
nonnegative integer vectors summing3,2,3:10×3×10=300 combinations.
Frequency=(3!/prod(a!))*(2!/prod(b!))*(3!/prod(c!)); sum2916=27×4×27.
Do not weight300 cases equally. Weighted condition counts remain18/12.
Each coffee vector serves training and opposite-fold evaluation; same vectors
for all arms. Refit every coefficient and source transform; retain all30
predictions even at zero evaluation weight. Save vectors, frequencies, fits,
predictions and scores. No Monte Carlo seed, draws or random sampling.
All-one case reproduces point predictions within declared numerical tolerance.

For each coffee use weighted condition-mean MSE. Aggregate RMSE is
sqrt(0.5*MSE_Cibao+0.5*MSE_Modœtia), not pooled conditions or mean RMSE.
Report RMSE/MAE/signed bias aggregate and both directions. Exactly five new
contrasts: D3/R3,D3/T2,D3/N,R3/T2,R3/N. Delta=L_A−L_B; gain=1−L_A/L_B.
Zero denominator gives undefined gain. Any positive-frequency undefined gain
makes the whole gain interval undefined; valid deltas retained, counts disclosed.
Construct the equivalent2916-value multiset by integer repetition; linear
2.5/97.5 percentiles, not weighted inverse-CDF quantiles. Save all intervals.

## Decisions, grades and influence

Primary aggregate D3−R3 delta: upper<0 gives
DURATION_OBSERVER_LOWER_CONDITIONAL_TDS_LOSS; lower>0 gives
PRESSURE_OBSERVER_LOWER_CONDITIONAL_TDS_LOSS; otherwise including zero endpoints
DURATION_PRESSURE_COMPARISON_UNRESOLVED.
Separately D3/R3 earns CONDITIONAL_PREFERENCE_OVER_TESTED_REFERENCES only if
aggregate delta upper<0 against each other arm, T2 and N AND its point RMSE is
no higher than every comparator in BOTH directions. Otherwise
NO_CONDITIONAL_OBSERVER_PREFERENCE, enumerating failed requirements, resolved
adverse comparators and directional disagreements. Reverse gains are recalculated
from losses. Incomplete inference forbids preference; zero is no equivalence margin.

Gain grades worse<0; small[0,.10); moderate[.10,.25); large≥.25. Report point
grade and every grade intersected by each closed interval for every direction.
All nine boundary combinations lower{.075,.10,.125}×upper{.1875,.25,.3125}
reclassify unchanged estimates. Descriptive conventions, not assay-error,
adequacy or acceptance thresholds; all decisions use unrounded values.

Exactly8 within-coffee grind-block and30 condition deletions; each removed from
both reciprocal roles. No cross-coffee joint deletions. Refit four arms/both
folds; report delta/gain ranges, exact ties and point-ranking reversals for all
five contrasts, aggregate and directions. Diagnostics, not CIs or model selection.
Total4×2×(1+300+8+30)=2712 fits,678/arm. QR/algebra checks occur within fits.

## Uncertainty, execution and handoff

Conditional95% resampling intervals have uncalibrated coverage; exact enumeration
removes Monte Carlo error only. Exchangeability of selected native grind blocks
within3/2/3 strata is assumed; independence/population sampling is unestablished.
Intervals condition on records, coffee pair, family and strata; nonsimultaneous,
not shot-level, measurement or new-coffee confidence. Measurement and coffee-
population CIs NOT_ESTIMABLE. Omit input error, actual within-condition means/
covariance, timing/chemistry covariance, instrument/aliquot preparation, sessions,
roast/lot/order dependence, shared systematics and prior selection. No adequacy,
causality, isolated pressure/kinetic effect, incremental value beyond all recipe/
grind information, autonomous prediction, blindness or production readiness.

Input qualification≤20minutes; science≤30minutes from first real fit, including
predictions/enumeration/deletions; dependency installation and required QA excluded.
Durable explicit fit start/finish records and counters; no restart/reset/retry,
renormalization, reduced enumeration or successful-case-only intervals. Stop on
source/join/operator drift, missing authority, leakage, failed reproduction,
rank/arithmetic/nonfinite failure, incomplete enumeration, budget exhaustion or
material unresolved defect. Save first failure, vectors and completed/unattempted
counts. Freeze binds inputs/operators, observations/order, folds/blocks, all300
vectors/frequencies, code/tests/methods, decisions, limits and inspection before
fitting. Private output outside Git and predecessors, located by locations.json.

Synthetic focused tests precede real fits. Required repository QA runs once in
an editable-installed environment; focused follow-up only for concrete failures.
Scientific completion, local QA and hosted status are separate; historical QA
records remain unchanged. Numerical verification is not independent human review.
Public files contain code/tests/methods/safe hashes only. Private RESULT≤750words,
SUMMARY≤120words, full JSON/CSVs, diagnostics/deletions/support/failure receipts,
FREEZE and verified ARTIFACTS. Draft PR stacked onPR384, unmerged, auto-merge off.

P1 blind-TDS=OPEN. One provisional successor only:
SCI-MD-PERTICARINI-HELD-GRIND-TDS-001, NOT_RUN. Justified only if conditional
preference is earned AND a concrete remaining unseen-native-grind prediction
decision is named; otherwise NOT_JUSTIFIED. ReassessP1/P3 if genuinely unexposed
existing data become executable. No successor execution or nearby family search.
