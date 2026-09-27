# Conditional tail spline — research model card

SCI-MD-MASS-DELIVERY-006. G1 / NO_GOVERNING_PHYSICS_CHANGE.
Written before implementation and real fitting. C2 CONDITIONAL_TAIL_SPLINE is
the fixed primary; C0 MASS_CONTEXT_TAIL_SPLINE and C1 FIRST_ASSAY_TAIL_SPLINE
are the only learned controls. No production registration or default adoption.

Let b be cumulative measured beverage kg from original source collection origin.
m1,m2 are measured first/second vial kg; q1,q2 are their mass-fraction assays
(source percent /100). Forecast anchor is m1+m2; no fitted clock/origin shift.
C0 consumes (m1,m2); C1 consumes (m1,m2,q1); C2 consumes (m1,m2,q1,q2).
Separate typed inputs reject extra fields, so an ablation cannot consume a
forbidden assay. Neither assay enters the suffix response loss.

For each fit, B_train is the largest valid suffix training endpoint. Exactly five
equally spaced linear hats H_j cover [0,B_train]. Features are centered by
training-only mean condition / mean shot values, then divided by fixed scales
(0.01 kg,0.01 kg,0.10 kg/kg,0.10 kg/kg), active prefix only. Include an intercept.
The same training domain/basis applies to all three arms. No condition IDs,
source labels, dates, recipes, final mass, future flow or whole-shot normalization
enter the regression. Training ranges only flag feature extrapolation; they do
not remove evaluation records or establish accuracy.

eta(b,z)=sum_j H_j(b)*(theta[j,0]+sum_r theta[j,r]*z[r]);
q_hat=sigmoid(eta); S_hat(a,c|z)=integral_a^c q_hat db;
TDS_hat_percent=100*S_hat/(c-a). Fit these interval averages, never midpoint
values or logits of observed averages. No per-query optimization, rate inversion,
or requirement to interpolate the early assays. The curve is empirical, bounded
and nonnegative; instantaneous concentration may rise or fall. Knot logits are
not rates, inventories, physical pools or bed states. Modeled cumulative delivery
is monotone, but gaps between assays remain modeled rather than measured solute.

Split integration at each actual knot. Within each segment eta is linear and
the integral is width*(softplus(right)-softplus(left))/(right-left). Implement
the equal limit sigmoid(left). For endpoint differences <=0.5, use
log1p(sigmoid(min_endpoint)*expm1(abs_difference))/abs_difference, avoiding
near-equal subtraction. For larger differences use sign-specific stable
softplus expressions (the positive pair uses the complement). Reject nonfinite
logits. Independent adaptive quadrature splits at knots and bisects each segment
for refinement (epsabs=1e-14 kg, epsrel=2e-13, limit=200). Allowance includes both
reference differences, both quadrature error estimates, and a 128-epsilon
width/solute roundoff term; zero-width allowance is zero. Every supported final
interval must have solute allowance <=1e-9 kg. Numerical sensitivity is neither
measurement uncertainty nor a statistical prediction interval.

Data loss = mean condition / mean shot / mass-weighted within-shot squared TDS
error in percentage points squared. Add exactly lambda *
(mean(nonintercept theta^2)+mean((second_difference(theta)/h^2)^2)), h=1/4.
The second difference runs along the five knots for EVERY coefficient column,
including intercept. Empty mean terms are zero (none of these arms is empty).
Every coefficient is bounded [-20,20]. lambda in {0.0001,0.01,1,100} only.
These are computational choices, not measured physical priors.

SciPy least_squares TRF, exact trust solver, linear loss, 2-point numerical
Jacobian, diff_step=1e-6, ftol=xtol=gtol=1e-10, x_scale=1, max_nfev=8000.
An independent residual-call counter counts ALL actual calls including numerical
Jacobian calls and stops each start before call 8001. Exactly three starts,
in order s=-1,0,1: slopes zero; knot intercept=logit(weighted training suffix
mean q)+s*(2*j/4-1). Initialization-only epsilon=1e-8 bounds that mean to
[epsilon,1-epsilon]; no source or prediction clipping. These starts satisfy
coefficient bounds. Lowest converged penalized objective wins; exact objective
ties keep start order. A converged start requires solver success, positive status,
finite coefficients/objective and no call/budget failure. Retain every start's
initial/final or last coefficients, status, termination, objective, residual calls,
Jacobian calls, boundary hits (distance <=1e-7), elapsed time and failure.

Condition-grouped leave-one-condition-out FIT development, all replicates and
fractions together. Canonical shared design labels must share a group. Fold
centering, domains, initializations and fits derive from the fold's TRAIN only.
Freeze coordinate/validity-only common held support per fold before any fitting.
All arms/lambdas share it; model failures cannot shrink it. For each arm select
minimum condition-balanced out-of-fold shot R; candidates with any failed fit or
prediction are NONSELECTABLE, not reduced error. Within 1e-6 pp of minimum prefer
larger lambda. These are development diagnostics, not unbiased nested validation.
Then fit each selected arm once on all FIT with the same three starts and freeze
all models. No outcome-triggered rescue, extra starts/features/knots or family.

Strict immutable serialized model includes coefficients, transforms, ordered
features/units, training/source hashes, domain, numerical settings, limitations
and rights. Immutable condition state embeds model identity and only permitted
early inputs. predict_intervals(state,starts_kg,ends_kg) needs only those windows;
remaining_solute(state,stop_mass_kg) integrates from the anchor. Before-anchor,
out-of-domain, unknown/nonfinite/reversed coordinates, invalid early inputs and
wrong units/basis fail. Zero width gives zero kg solute and undefined average TDS.
Save/load verifies schema, exact fields, derived state and content hashes.

Frozen FIRST_ASSAY_EMPIRICAL from 005 is a historical reference: unchanged
coefficients, kernel, runtime and domain [0,0.06350639999999999] kg. Reuse retained
predictions where available, requiring exact identities and coordinates; generate
previously absent stress predictions using that same frozen operator. Recompute
only 006 metrics on exact common support. It differs in training data from C0/C1,
so its comparison does not isolate the same information ablation.

RESEARCH_ONLY / SOURCE_INTERNAL / TARGET_EXPOSED /
RETROSPECTIVE_CAMPAIGN_SEPARATED_CONDITIONAL_PREDICTION.
Prior campaign exposure cannot be undone. No fresh blind holdout, independent
validation, mechanism identification, universal coffee behavior, measured whole-cup
total, inventory closure or prediction of hydraulics is claimed.
PHYSICAL_VALIDATION=NOT_ESTABLISHED. Pannusch/Schmieder, Mendeley
10.17632/y2tz67f6ry.1, source-derived CC-BY-NC-3.0 treatment remains separate from
first-party software licensing.
