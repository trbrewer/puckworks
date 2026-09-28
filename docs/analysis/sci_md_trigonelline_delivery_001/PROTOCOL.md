# Fixed trigonelline delivery comparison

SCI-MD-TRIGONELLINE-DELIVERY-001; G1; RESEARCH_ONLY;
NO_GOVERNING_PHYSICS_CHANGE. This protocol is committed before real fitting.
Its arms, information sets, thresholds and numerical rules cannot change after
fitting starts. Source-derived results retain CC-BY-NC-3.0 restrictions.

## Question and information boundary

Test exactly TR-K0 and TR-D0 against original later trigonelline assays,
conditional on measured beverage mass. Inference accepts only `m1_kg`,
`m2_kg` and requested measured-mass coordinates. Neither early nor later TDS,
caffeine or trigonelline, recipe, time, pressure, nominal flow, density or
inventory may be an inference input. A trigonelline observation may enter only
the declared FIT training or the single approved PRED outcome join.

SOURCE_INTERNAL / TARGET_EXPOSED / RETROSPECTIVE_CAMPAIGN_SEPARATED_CONDITIONAL_PREDICTION.
This is not fresh-blind or independent-source validation. No universal
transfer, whole-cup closure, H1, equilibrium or kinetic inference is supported.
Trigonelline is a constituent of TDS, not additional TDS. Numerical
qualification is not physical validation. Analytical measurement uncertainty
is NOT_ESTABLISHED and is not replaced by these engineering budgets.

## Frozen source population

Pannusch 2024 / Schmieder 2023 shared source lineage is counted once. Use the
accepted originals resolved by the existing local source resolver and exact
SOURCE_IDENTITIES.json hashes; no replacement download or new acquisition.
Trigonelline is MATLAB `cAlcaloids(:,2)`, HPLC workbook column T, reconstructed
as mg/fraction divided by that original vial's measured mass in g, giving
mg/g beverage. The qualified original dilution/calibration formulas and
validity/exclusion semantics are retained in DATA_AVAILABILITY_PREFLIGHT.json.
No imputation, censor substitution, observation edit or mass-prefix filling.

FIT is the existing 45-physical-shot, 15-original-design campaign. Target
fractions are exactly 3, 5, 7 and 10. Preserve all 180 intended slots and
statuses. All 180 are source-valid; 177 have qualified measured mass support;
three retain UNAVAILABLE_MEASURED_MASS_PREFIX. Every design must retain at
least two physical shots with at least three qualified target windows each.
All shots/fractions of one original design stay together in a fold.

Primary PRED is C01, C02, C05, C06: 12 original physical shots and all 48
intended windows, each source-valid and within the frozen common domain.
Temperature C03/C04 and flow C07/C08 are secondary only. Retain all 96 PRED
slots per arm, including the one unsupported flow window. Secondary panels
cannot select models, hyperparameters or thresholds. No favorable exclusions.
Original measured vial masses, including intervening unassayed vials, define
the cumulative mass coordinate; no time-to-mass or nominal-flow substitution.

Target-blind integrity checks may inspect finite/valid metadata and reconcile
source bytes silently. PRED values or concentration patterns cannot influence
design, fitting, preprocessing, selection or support. Training, coordinate-only
queries/predictions, and outcome-join artifacts remain separate and private.

## Exactly two arms

TR-K0 is one nonnegative constant concentration equal to the training weighted
mean. Both arms use the same hierarchy: equal total weight per original
design, equal total weight per physical shot within design, and interval mass
weight normalized within shot over qualified supervised windows. TR-K0 is an
analytic fit without an optimizer or tuning parameter.

TR-D0 adapts the accepted caffeine D0 architecture without caffeine
coefficients or a TDS parent. Let B be the maximum qualified training endpoint.
Five equally spaced knots on [0,B] define linear hat functions. The pointwise
concentration is the logistic of interpolated knot logits. Each knot logit is
`theta[j] @ [1, (m1-mean1)/0.01, (m2-mean2)/0.01]`. All 15 coefficients are
bounded by [-20,20]. Training-only shot/design weighted mass means and feature
minima/maxima are saved. The hard mass support and knot domain come only from
the retained training rows in that fold. Feature-range extrapolation is
reported explicitly; it does not create a favorable exclusion.

The data residual is `(1000/0.25)*(predicted_q-observed_q)*sqrt(weight)`, with
q in kg/kg. The inherited penalty is lambda times the mean squared mass-feature
slopes plus lambda times the mean squared second knot differences divided by
0.25 squared before squaring. Lambda is exactly [0.0001,0.01,1,100].
Initialization is the logit of the weighted training concentration bounded
to [1e-8,1-1e-8] for initialization only, with zero feature slopes and intercept
ramps -1, 0, +1 times linspace(-1,1,5), in that order. Observations and
predictions are never clipped.

Use scipy least_squares with trf, exact trust-region solver, linear loss,
2-point numerical Jacobian, diff_step=1e-6, x_scale=1, and
ftol=xtol=gtol=1e-10. max_nfev is 8000, additionally bounded by 8000 actual
residual calls including numerical-Jacobian calls. Retain every start, status,
objective, call count, wall time and boundary coefficient. Lowest finite
converged objective wins; exact ties use start order. No rescue starts.

## Development and final fit

Run fixed leave-one-original-design-out development over all 15 designs.
Derive preprocessing, knots and support separately from each fold's training
rows. No chemical outcome from an excluded design may affect that fold's model
or preprocessing. Freeze coordinate-only held support masks before fitting;
record every original held slot and reason. Evaluate each declared lambda on
the same fold masks using mean physical-shot mass-weighted RMSE in mg/g,
then mean equally over held designs. Development is not unbiased nested
validation. Select the largest lambda within 1e-6 mg/g of the minimum balanced
development RMSE, exactly as inherited. A lambda requires every fold to be
numerically selectable. Record all fold and start failures; budget failure
stops execution. No extra features, search, threshold or family.

Fit the selected TR-D0 once on all qualified FIT windows with the three
declared starts. Fit TR-K0 analytically on that same population and hierarchy.
At most 180 development plus three final iterative starts; at most 16 analytic
K0 fits if the constant is also reported in each development fold.

## Numerical contract

Internal beverage and analyte mass are kg; concentration is kg/kg.
`mg = 1e6 * integrated_trigonelline_kg` and
`mg/g = 1000 * integrated_trigonelline_kg / interval_beverage_kg`.
Inference rejects nonfinite inputs, wrong species/units/schema, extra chemical
features, reversed intervals, queries before m1+m2, or queries above the saved
hard domain. Zero-width intervals have zero analyte mass and undefined
concentration. Model and state serialization are strictly trigonelline-tagged.

Integrate with 64-point Gauss-Legendre quadrature split at the fixed knots;
compare with 128 points and independent adaptive quadrature, also split at
knots (epsabs=1e-14 kg, epsrel=2e-13, limit=200). The integral allowance is
max(|I64-I128|, |I64-Iadaptive|+adaptive_error,
|I128-Iadaptive|+adaptive_error) +
128*machine_epsilon*(interval_width+|I64|).
Preserve the accepted fraction-3 source-anchor reconciliation only: a source
start differing from m1+m2 by at most four ULPs may use the anchor, with an
additional allowance of twice the absolute displacement. No general clipping,
expanded tolerance, geometry repair or altered support is allowed.
Every evaluated interval allowance, including this term, must be <=1e-9 kg.
Unqualified primary numerics stop the comparison before scoring.

Convert each interval allowance to mg/g using its measured beverage mass.
For shot RMSE propagate the weighted L2 norm of these allowances; for signed
and absolute bias use the weighted L1 sum. Average allowances over the same
original shots and conditions. Gain differences add allowances; relative gain
uses the bounded equivalent D0_R <= 0.85*K0_R. Report numeric lower and upper
bounds, with nonnegative lower bounds for nonnegative metrics. Application
allowances are not statistical confidence intervals or analytical uncertainty.

## Single frozen comparison and acceptance

For error e_i = predicted minus observed concentration in mg/g and measured
interval mass w_i, R_shot = sqrt(sum(w_i*e_i^2)/sum(w_i)) and
B_shot = sum(w_i*e_i)/sum(w_i). For each condition, R_condition is mean R_shot
over its three ORIGINAL physical shots; A_condition is mean abs(B_shot) over
those same shots. Balanced summaries average equally over original conditions.
Never average signed biases before taking their absolute values. Missing or
invalid slots cannot improve a denominator or a full-scope summary.

Each arm is adequate only if every primary condition has R_condition <=0.25
mg/g and A_condition <=0.125 mg/g. Use numerical upper bounds for PASS;
a lower bound exceeding a limit is FAIL; overlap is UNRESOLVED. Do not round
into a verdict. These are engineering research budgets, not measurement
uncertainty, health limits or statements about taste.

TR-D0 earns complexity only if adequate and all four conditions hold:

- balanced R improvement over TR-K0 >=0.05 mg/g;
- balanced R improvement >=15%;
- at least three of four primary conditions are definite R wins
  (D0 upper R strictly below K0 lower R);
- balanced mean absolute shot bias deteriorates by <=0.025 mg/g.

All inequalities use propagated numerical bounds. A conjunction is FAIL if
any requirement definitely fails, PASS only if all pass, otherwise UNRESOLVED.
If the primary comparison is qualified and resolved, report in this order:
TRIGONELLINE_MASS_SHAPE_EARNED when D0 earns complexity;
CONSTANT_TRIGONELLINE_BASELINE_ADEQUATE when K0 is adequate;
TRIGONELLINE_D0_ADEQUATE_INCREMENT_NOT_ESTABLISHED when only D0 is adequate
without earned complexity; TESTED_TRIGONELLINE_BASELINES_INADEQUATE when both
arms are definitely inadequate. An unresolved arm adequacy or unresolved
required complexity decision reports NOT_ADJUDICATED with the exact blocker.
An adequately completed negative comparison is task SUCCESS, not NULL.

Generate the entire coordinate-only matrix before outcomes are attached.
Freeze all identities, protocol/code/runtime, preprocessing, support, models,
states and predictions. One genuine independent exact-freeze approval is
required before the exclusive score-start receipt and sole outcome join.
No approval means READY_FOR_INDEPENDENT_REVIEW. No self-approval or invented
review authority. Preserve the reviewed scientific producer identity separately
from later publication commits. A post-score scientific defect requires
withdrawal and new authority; no tuning, prediction repair or rescoring.

`verify` checks retained identities and replays saved-model inference without
fitting, joining outcomes or creating a score. `report` reads the retained
completed score, never recomputes the experiment. Source originals and
row-level observations/predictions stay outside Git; only sanitized aggregate
evidence, models and bindings may be published.

## Hard stops and scope

The PLAN.md six-hour task deadline and 60-minute fitting, 183-start,
8000-call/start, one-worker/thread, 12-GiB process and 5-GiB private-evidence
budgets are hard ceilings. Counters and incomplete attempts are durable.
Stop for duplicate/ownership/authority conflict, failed baseline, missing or
mismatched source, insufficient primary/FIT support, unresolved analyte or
censor semantics, unqualified numerics, budget excess, need for another family,
parent retuning, acquisition, or inability to obtain independent approval.
No author contact, lab commissioning, EWP consumer, production change, merge,
adoption or successor is authorized. NATIVE_EWP_RUNS=0.
