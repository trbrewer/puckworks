# SCI-MD-MASS-DELIVERY-002 protocol

Owner-authorized G1 / NO_GOVERNING_PHYSICS_CHANGE. Puckworks issue #279;
EWP issue #185. One task PR per repository, OPEN/UNMERGED for owner disposition.
No native simulation/build, production/default/lock change, merge or successor.

## Starting point and selection

Puckworks base 69f9ef3453294709ef575d63b156d9d78c49d2db, tree
24ebe16623b350f8e4f3fd04b7ecbf241c9a03a8. EWP base
386cba18c421d4f0944450f412fd055ca2127a19, tree
b255367805d527bfd04c36426ae1435aae9656c8. Live #278/#184 are MERGED on
2026-09-26. Their squash-merge trees equal the recorded predecessor PR-head
trees; those head commits need not be ancestors of the squash commits.
Clean task worktrees preserve unrelated work and every 001 artifact.

NEW_INFORMATION: whether nominal recipe conditioning improves the absolute
TDS mapping beyond exposed MASS-DELIVERY-001 with a fair setting-aware baseline.
POSITIVE: retain an adequate research predictor with earned complexity only if
A/B/C pass. NEGATIVE: retain the honest negative and, if adequate, empirical
predictor. BLOCKED: identify the named source/support/numerical/review gap.
GRINDER_TO_CUP_LINK: conditional delivered-solute outputs, no hydraulic claim.
REPEATED_BLOCKER: inventory and hydraulic mapping are not needed for this
observable; existing measured masses, TDS and design settings answer the named
question. LOWER_COST_ALTERNATIVE: reuse qualified reconstruction and kernel.
No general data-exhaustion, laboratory or automatic successor recommendation.

## Source contract and information flow

Use existing Puckworks external configuration and source hashes, reconstruction
DoE reader, assay identities and complete measured mass prefixes. FIT_2021_12:
experiments 9/10/11/14/15, grind 1.7, dose 20 g, five conditions/15 physical
shots/90 TDS observations. Sites (C,code): C09=(89,2), C10=(89,1), C11=(89,3),
C14=(80,2), C15=(98,2). Primary PRED-C01=(86,2), C02=(92,2), C05=(90,1.7),
C06=(90,2.3): four conditions/12 shots/72 observations. Validate identity sets,
not only row counts. Other grinds and exp46 never enter fitting. No pooling of
Pannusch and related Schmieder as independent cohorts.

Intervening unassayed vials advance mass; missing chemistry is not zero.
S_obs=measured_beverage_kg*TDS_percent/100. Assayed-support totals are not measured
whole-cup totals. Apply TDS-specific validity; HPLC issues do not invalidate TDS.
Keep source dates and UNKNOWN/UNRESOLVED coffee/roast metadata in evidence.
Reconstruct target coordinates/features without attaching target chemistry.
PRED-C03/C04/C07/C08 remain NOT_ADJUDICATED_VARIABLE_SETTING_INPUT. Preserve their
historical 001 results without new ramp scoring or dilution of the primary set.

Setting qualification uses both hash-verified ExpSheet designs (FIT Flow (ml/s)
and Temp (°C); March Flow_0/Flow_E and T_0/T_E), their common DoE axis,
qualified experiment/program registers and reconstruction mapping. The common
DE1/source design and matched nominal collection-design conventions establish
source-design meaning, not measured flow. Source preprocessing stores measured
or fitted run.flow separately. The feature is solely a dimensionless nominal
code; no TDS, run.flow, derivative, inferred boundary or density conversion.
Unresolved interpretation blocks the full primary comparison, not a substitute
reduced success. Historical physical-flow mapping remains unresolved.

## Frozen models, fitting and CV

MODEL_CARD.md defines the exact MT/MF/MTF and SETTING_AWARE_EMPIRICAL mathematics.
M0 is frozen 001 MASS, SHA256
75aa34648f73883e975b16c2267594a247142e247713f14642641789f5e2182d.
Old setting-blind empirical scores are historical context only. No TIME search.
No campaign/shot amplitudes, offsets, first-fraction calibration, interactions,
quadratics, condition-specific shape, extra pools or random effects.

Three whole-shot folds hold R1, R2, R3 respectively from every FIT condition.
This is within-setting replicate cross-validation, not unseen-setting prediction
or independent validation. All fractions of a shot stay together. Fold domains
and shared equally spaced knots use only that fold's training b1 maximum.

Residual_i = 100*(S_pred_i/m_i-q_obs_i)*
sqrt(m_i/(C*n_c*sum_eligible_assayed_m_in_shot)). Objective is sum residual_i^2.
Thus mass weighting within shot, equal shots within condition, equal conditions.
No target-derived normalization. Fit-stage APIs reject non-FIT chemistry.

Compact TRF least_squares: 2-point Jacobian, exact trust solver, linear loss,
ftol=xtol=gtol=1e-10, diff_step=1e-6; x_scale=[.2,50,1,1,1,1,1] active subset.
STARTS.json freezes literal 16 seven-parameter arrays before fitting: eight
inherited starts with zero slopes plus eight PCG64(2026092602) uniform starts
under the recorded bounds. Project inactive slopes to zero for ablations.
No all-FIT coefficients initialize held-fold fits. Select lowest converged
objective, ties by start index. Record failures, termination, calls, parameters,
boundary hits and local Jacobian rank/singular values/conditioning.
Planned 3*4*16=192 nonlinear starts; hard total 500 including corrected/failed
attempts, tracked in persistent external ledger; hard 2000 actual residual calls
per start including initial and numerical Jacobians. No optimizer expansion.

Empirical K in {5,9}; lambda in {0,.001,.1,10}. At each of five sites fit exact
integrated hat-basis averages with coefficients [0,1]. For x=b/B,h=1/(K-1),
penalty per site=lambda*mean((100*D2(q)/h^2)^2); average the five site penalties
alongside the balanced observation objective. Equivalent independent site
solves multiply the site observation weights by sqrt(5). No monotonicity.
Bounded TRF lsq_linear tol=1e-12,max_iter=1000. Count actual linear solves
separately; record data and augmented design rank/conditioning. Any unpenalized
candidate with rank<K at any required site/fold is excluded, not treated as
identified. Failure or unavailable candidate is retained explicitly.
All admissible candidates use the same held-interval support subset per fold;
validate support masks and report original shot/condition/assay denominators.
Select lowest balanced held-shot mean RMSE averaged over folds. Ties <=1e-10 pp:
fewer knots, then stronger smoothing. Partial-support CV is diagnostic only.
One all-FIT fit for selected empirical hyperparameters and each compact family.

Final mass endpoint must equal predecessor 0.0635064 kg (floating tolerance
1e-15 kg); no March expansion. The mass-domain/design-diamond product is a
modeling assumption. Report each site measured extent and profile/curve use
beyond that site's extent. No rectangular hull substitution or extrapolation.

## Numerics, audit and scoring

Reuse 128-point u=v^8 Gauss-Legendre kernel, 256 refinement, exact constant limits,
independent adaptive quadrature epsabs=1e-13 kg,epsrel=1e-11,limit=200. Empirical
independent integration splits at knots. Allowance=max(refinement difference,
independent difference+reported error,1e-17 kg), zero for zero width. Each
supported interval requires allowance<=1e-9 kg. Propagate allowances by triangle
inequalities into RMSE/bias and comparisons, not as measurement uncertainty.

Freeze code/protocol/source/split identities, artifacts, empirical selection,
all five primary prediction matrices, support/exclusions/thresholds before
independent pre-score review. Existing independent reviewer mechanism and receipt
format apply; implementation author cannot approve. If unavailable, stop with
tested frozen preparation and unexecuted scoring. After approval: one scoring
invocation; no target-informed fitting, exclusions, selection or adjustments.
Replay M0 against 001 condition and balanced R/B within 1e-9 pp (above displayed
JSON rounding and propagated numerical noise); mismatch blocks scientific
verdict without retuning. Preserve failed attempts and original evidence.

Shot e_i in TDS pp; R_j=sqrt(sum(m_i*e_i^2)/sum(m_i));
B_j=100*sum(S_pred_i-S_obs_i)/sum(m_i). Average shots per condition, then
conditions equally. A: every primary condition mean R<=1.00 pp and mean abs(B)
<=.50 pp, complete eligible support and numerically qualified decisions.
B: vs M0 >=20% balanced R reduction AND >=.10 pp reduction AND lower condition
R in >=3/4 AND balanced mean abs(B) deterioration<=.10 pp.
C: A AND R_MTF<=R_empirical+.10 AND absB_MTF<=absB_empirical+.10 pp.
D: separately apply B against empirical. These are working margins, not
statistical equivalence. Propagated threshold intervals crossing the threshold
are NUMERICALLY_UNRESOLVED. CONDITIONING_EARNED only when MTF A/B/C all PASS;
otherwise report axes separately and whether inadequate, empirical preferable,
adequate without gain, or source/support/numerical comparison unresolved.
MT/MF remain ablations even if they succeed. Unsupported original records and
conditions stay visible; partial denominators cannot earn adequacy.

SOURCE_INTERNAL; TARGET_EXPOSED; RETROSPECTIVE_MODEL_DEVELOPMENT_COMPARISON.
Task selection used exposed predecessor results. March is not newly blind.
Predictive adequacy does not identify parameters, mechanisms or causal effects.
Source-derived models/aggregates remain CC-BY-NC-3.0 with Pannusch/Schmieder
attribution, Mendeley 10.17632/y2tz67f6ry.1; first-party code licensing separate.
Raw source, row-level tables and full logs stay private. PHYSICAL_VALIDATION =
NOT_ESTABLISHED; NATIVE_EWP_RUNS = 0; PRODUCTION_DEFAULTS_CHANGED = false;
PRODUCTION_DEPENDENCY_LOCK_CHANGED = false; NO_SUCCESSOR_AUTHORIZED.
