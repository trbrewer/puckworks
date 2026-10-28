# SCI-MD-WADSWORTH-PERCOLATION-KC-TRANSFER-001

G1 / RESEARCH_ONLY / NO_GOVERNING_PHYSICS_CHANGE. Owner-authorized conditional
representation comparison. Exactly PER1/KC1/N/S3; PER1/KC1 is the matched
one-coefficient primary comparison. S3 has three coefficients and is explicitly
a higher-capacity benchmark. Historical PR381/PR382/PR383 and closed mass-delivery
decisions remain unchanged. One implementation/review cycle, at most one material
pre-score correction; input qualification <=20 minutes, scientific computation
<=30 minutes from first real fit. Installation and required QA are outside those
caps. No new acquisition, experiments, figures, native EWP runs, extra families,
exponent search, tuning, parameter bounds or outcome-driven rescue.

## Pinned authority and inspection

Main `21669a427145194e1f4003e3cf1b97dedefe2679`; base PR383
`6a97530d746269cf9e9d46dbcbdfd83e54a2caf5`; its parent/scientific predecessor
PR382 `9f311e70bd08ae16387c9ac40aa9c71595f95a65`; read-only EWP
`f44c33dbb9b4fb80143e360e6f4a90f8ac0aa516`. Isolated worktree; predecessors,
source bytes, registered gates and production defaults remain unchanged.

Source SHA256 `3b0139fe02108d3dfcd1441d9e4062e86d9b7e1a8505141a7beefd9366ebf20f`;
blob `37b4136bfa1a84df159f41c01245000288db4ebf`; 2315 bytes/23 CRLF.
Ordered membership `f72c57505fab4b7bf42876970c89207b36f3f1975e0b79081b09ca10563a8821`;
observations `901e04ce19ab3b29a1a77f7617e5f975c70f661fa7579df1d9a335f6527c68e2`;
PR382 folds `5b5966ceeaf0cd815cd6bfb69237461bffb30bc3193b8d74406ee592950b63f4`.
Authenticate PR382 FREEZE `f44693c947ddae7a62a503bbdcbeb8a97406fb5b07ae49d196b9feef0161e2d9`
and RESULT `35d44b6a42429374cc7c2643062cc3c00b1623919721af02ab2150bae9ea3e3e`
before trusting contents. Verify their relationship, all 11 frozen scientific
files, complete observations, ordering and reciprocal roles. A newly read
manifest is checksum consistency only; PR381's manifest is not PR382's anchor.
The pinned PR382 status independently binds its saved-arithmetic verification,
which does not itself bind draw bytes. Draw comparisons are therefore labelled
unanchored numerical consistency; anchored RESULT interval reproduction remains
mandatory. Never call predecessor authenticate_parent/reproduce unchanged.

Read repository instructions, available-data policy/register, specified source,
code, methods, status, tests, card, provenance and permissions. Private inspection
receipt lists actual cells/artifacts. The owner explicitly authorized searching
for the task-named retained bundle after initial scoped locator checks failed;
private paths/configuration are not published. No uninspected original-paper or
raw XCT authentication is claimed. Equation authority is the supplied fixed
equations, existing native k_star/B_PERC and Wadsworth et al., RSOS 13,252031,
DOI 10.1098/rsos.252031, §§2.2,3.5,4.3. Attribution and CC BY 4.0 are retained;
derived calculations are new and private, with no broader rights clearance.

## Records, equations and fitting

Retain all 22 preparation identities and original ordering; exactly 21 endpoints:
Guayacan10/Tumba11. Guayacan G2 stays excluded for missing connected geometry and
response. Two coffees, ZERO espresso shots. Only phi_p_connected (0<phi<1),
s_p_connected_per_m (finite positive m^-1) and k_m2 (finite positive m²) enter
models. Radius and k_err are provenance only. No total-geometry substitution,
radius-derived surface, polydispersivity, imputation or row fusion.

k0=1e-10 m², s0=1e4 m^-1; z=ln(k/k0), t=ln(s/s0), u=ln(phi).
g_PER=ln(2/(k0*s0²))+log1p(-phi)+4.4u-2t;
g_KC=ln(1/(5k0*s0²))+3u-2t.
PER1=g_PER+c_PER; KC1=g_KC+c_KC; N=c_N; S3=c+a*t+b*u.
Each intercept is its independent source-weighted mean residual; S3 independently
minimizes identical weighted log SSE. One unrestricted coefficient for PER1/KC1/N,
three for S3. Fixed exponent4.4, threshold0; no global alpha4808, global fit,
clipping, sign constraints, ridge or target-derived transform. Constants2/5 are
absorbed by calibration, so this tests porosity shapes at common measured surface,
not untuned normalization or a universal Kozeny constant.

Exactly Guayacan10->Tumba11 and Tumba11->Guayacan10. Every retained endpoint has
one held prediction per arm. Float64, finite nonnegative source weights with
positive finite sum; individual zeros allowed. S3 uses the accepted weighted
centering/population scaling and SVD solution, with independent QR. Full rank:
singular value > eps*max(active weighted matrix shape)*largest singular value.
No rank-deficient fallback. Analytic intercepts independently checked by weighted
one-column QR. Save coefficients, transforms, SSE, rank, singular values,
conditioning and discrepancies keyed by training coffee and arm.

Finite source/target predictions, inverse coefficient maps and checked
exp(ln(k0)+z_hat) are mandatory; prediction discrepancies <=1e-9*max(1,abs(z_hat)).
S3 SSE <= KC1/N SSE +1e-12*max(1,comparator SSE); PER1 is not nested in S3.
Verify PER1-KC1=d(phi_target)-weighted_mean_source(d(phi)), where
d(phi)=ln(10)+log1p(-phi)+1.4ln(phi). Surface and source responses cancel from this
prediction difference; observed permeability still determines scored differences.
Retain extrapolations and zero-weight target predictions. Save active-source
marginal ranges and target flags; marginal containment is not joint support.
Analytic/rank checks suffice; no jaxgsa campaign or physical identifiability claim.

## Reproduction, scores and paired inference

Within this ONE campaign, reproduce S3/N point predictions (absolute tolerance
1e-10), every recorded point score and aggregate/directional loss intervals and
S3/N contrast summaries against pinned RESULT. Score tolerance is
1e-10*max(1,abs(parent)) for dimensionless values and
1e-10*max(k0,abs(parent)) for m² values. Available saved draw S3/N predictions,
scores and multiplicities are compared inline as unanchored numerical consistency.
No separate historical campaign or E3/W3 refits.

Primary L=sqrt(.5*MSE_Guayacan(log error)+.5*MSE_Tumba(log error)); weighted means
within coffee, not pooled21 or averaged directional RMSEs. Also report aggregate
and directional log RMSE/MAE/bias and absolute m² RMSE/MAE/bias from SAME fits.
Exactly five new contrasts: PER1/KC1, PER1/N, KC1/N, PER1/S3, KC1/S3.
S3/N is reproduction/context only. Delta=L_A-L_B; gain=1-L_A/L_B. Zero reference
loss makes gain undefined without epsilon. Any undefined draw makes its whole
gain interval undefined; retain delta and disclose counts. Reverse delta CIs
as [-upper,-lower]; reverse gains are recalculated from losses, never negated.

Exactly2000 full-refit draws: SeedSequence(20261027).spawn(2), default_rng streams
Guayacan,Tumba. Draw n indices via integers(0,n,size=n), bincount(minlength=n),
n=10/11. ONE vector per coffee serves training and opposite-fold evaluation;
identical across all arms. Refit all coefficients/transforms; save all endpoints
even with zero evaluation weight. Linear 2.5/97.5 percentiles, marginal conditional
95% intervals in aggregate/both directions/both units. Stop on first required
failure; save vectors, diagnostics and requested/completed/failed/unattempted/
undefined counts. No retry, reseed or successful-only/reduced inference.

## Decisions, grades and bounded influence

PER1-minus-KC1 aggregate log delta upper<0: PER1_LOWER_CONDITIONAL_LOG_LOSS_THAN_KC1;
lower>0: KC1_LOWER_CONDITIONAL_LOG_LOSS_THAN_PER1; otherwise including zero:
CALIBRATED_SHAPE_COMPARISON_UNRESOLVED. Separately either shape earns
CONDITIONAL_PREFERENCE_OVER_TESTED_ARMS only with aggregate delta upper<0 against
the other shape, N AND S3, plus point loss no higher against each in BOTH
directions. Otherwise NO_PUBLISHED_SHAPE_CONDITIONAL_PREFERENCE; enumerate failed
requirements, resolved adverse comparators and directional reversals. Report each
shape/S3 comparison explicitly; never automatically grant S3 overall preference.
Repeat as labelled absolute-unit sensitivity; it cannot replace log primary.
Incomplete inference precludes preference. Zero is discrimination, not equivalence.

Descriptive gain grades: worse<0; small[0,.10); moderate[.10,.25); large>=.25.
Report point and every grade intersecting closed CI. Reclassify unchanged estimates
at all nine {.075,.10,.125} x {.1875,.25,.3125} boundaries. No measurement-error
or practical-adequacy interpretation. Exactly21 record deletions and11 setting
deletions remove both reciprocal roles, retaining actual G2 missingness; refit
all four arms twice. Save delta/gain ranges, exact ties and point-ranking reversals
for five contrasts, all directions/both units. Influence is not CI; shared grind
labels are not independent replication. Exactly16264 arm-by-coffee fits,4066/arm;
independent algebra/QR checks occur within these fits. No additional sensitivity.

## Exposure, uncertainty and completion

SOURCE_INTERNAL / TARGET_EXPOSED / RETROSPECTIVE /
CONDITIONAL_ON_TABULATED_CONNECTED_SURFACE_AREA_AND_POROSITY; N has no morphology
predictor. Prior means/summaries are exposure. TDS/EY NOT_APPLICABLE; no density
conversion. Morphology and LB permeability share XCT geometry. k_err is
directional variation, not noise calibration or independent replication; never
inverse-variance weights or simulated noise. Conditional resampling coverage is
uncalibrated, not simultaneous or adjusted for prior model selection.
Measurement/coffee-population CIs NOT_ESTIMABLE. Exclude correlated geometry/
segmentation error, directional uncertainty, replication, shared systematic
effects and prior representation selection. No wet-puck, espresso, causal,
physical-law, independent-LB-validation, blindness, adequacy or production claim.

Before first real fit, private FREEZE binds identities, authority, observations,
folds, code/tests/methods, inspection, equations, seeds, metrics, numerics,
decisions/grades and budgets. Public Git contains only five task code/test/method/
safe-status files. Private RESULT<=750 words/~2 pages; SUMMARY<=120 words; complete
JSON/CSVs, all draws/diagnostics/deletions/reproduction/failure receipts and SHA256
ARTIFACTS. No imported ARMS/PAIRS mutation. Stop on missing/drifted authority,
operator/identity mismatch, leakage, reproduction/rank/arithmetic/nonfinite failure,
incomplete inference, budget exhaustion or unresolved material defect.

Synthetic tests precede fitting. Install project before child-CLI QA. Run required
repository QA once, focused follow-up only for concrete failures; report local
and hosted separately. Preserve PR381 failures, PR382 repair and PR383's initial
failed-suite/full-suite-not-repeated record. Numerical checks are not human review.
Draft PR stacks on PR383, stays unmerged with auto-merge disabled, directly verified.
P1 blind-TDS=OPEN. Sole provisional successor, NOT_RUN:
SCI-MD-WADSWORTH-SOLID-FRACTION-PREFACTOR-001 (fixed log1p(-phi)+S3 versus S3).
It needs a separately named remaining model decision; unresolved results alone
do not justify it. Otherwise NOT_JUSTIFIED. Reassess P1/P3 only if genuinely
unexposed existing data become executable.
