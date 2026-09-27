# Caffeine interval delivery — research model card

SCI-MD-CAFFEINE-DELIVERY-001. G1 / NO_GOVERNING_PHYSICS_CHANGE.
Prospective task-local contract, written before implementation or real fitting.
This is supervised observable modeling, not a multispecies inventory model.

Let b be cumulative measured beverage kg from the original collection origin,
a=m1+m2, and T(b;z) the unchanged SCI-MD-MASS-DELIVERY-006 C2 curve.
Four fixed arms: D0=sigmoid(eta_D(b;m1,m2)); S0=r*T(b;z), 0<=r<=1;
S1=T(b;z)*sigmoid(eta_1(b;m1,m2)); S2=T(b;z)*sigmoid(eta_2(b;m1,m2,q1,q2)).
S2 is primary. S1 already indirectly uses early TDS through C2; S2-vs-S1
isolates additional composition conditioning. D0 requires no TDS or parent state.
Caffeine is part of TDS, never additional total dissolved mass or an EWP source.
The share constraint is a model constraint, not measured chemical closure.
D0 ordering violations against predicted TDS are reported without clipping.

Five equally spaced piecewise-linear logit hats on the inherited parent [0,B]
knots. Every knot has an intercept and standardized linear feature slopes.
No interactions, extra knots, recipe/time/condition features or extra families.
Use verified parent training-only means/ranges for applicable features, with
fixed scales .01 kg,.01 kg,.10 kg/kg,.10 kg/kg. Fold parent lambda=.0001.
Head hard upper support=min(parent B,largest eligible caffeine TRAIN endpoint);
retain the parent knot locations even if this restricts the output domain.
D0 uses identical domain and knots. No PRED extrema enlarge training support.

The objective is sum_d 1/N_design sum_s 1/N_shot(d) sum_i
[m_i/sum_k m_k]*( (1000*qhat_i - observed_mg_g_i)/.50 )^2
+ lambda*[mean(theta[:,1:]^2)+mean((diff(theta,n=2,axis=0)/(.25^2))^2)].
Second differences include intercept and every slope. Empty means are zero.
Weights use only eligible training windows and preserve design/shot hierarchy.
All theta coefficients bounded [-20,20]. Lambda grid {.0001,.01,1,100}.
S0 solves r=clip(sum_i w_i*x_i*y_i / sum_i w_i*x_i^2,0,1),
x_i=predicted interval-average TDS kg/kg, y_i=observed caffeine kg/kg,
with the same weights. Zero denominator is an explicit failed fit.
Record unconstrained r and boundary solutions. Never average observed ratios.

Exactly three deterministic starts s=-1,0,+1 per iterative fit, all slopes zero,
intercept_j=logit(clamp(u,1e-8,1-1e-8))+s*(2*j/4-1).
D0 u=sum(w*y); S1/S2 u=sum(w*y)/sum(w*x), using only training
caffeine and the designated fold parent predicted TDS. Clamping is initialization
only, never observations/predictions. Reject out-of-bound initialization.
SciPy least_squares: TRF/exact, linear loss, 2-point Jacobian, diff_step=1e-6,
x_scale=1, ftol=xtol=gtol=1e-10, max_nfev=8000; independently count actual
residual calls including numerical Jacobians, abort before call 8001.
Lowest finite converged penalized objective wins; exact ties keep start order.
Record every start, failure, boundary coefficient (within 1e-7), calls and time.
No extra starts or rescue fits. A hard budget failure makes the fit nonselectable.

Leave one ORIGINAL DESIGN out, all physical shots/fractions together.
Reuse retained C2 fold model at .0001 excluding that design for BOTH head training
and held prediction. Verify its retained file/content hashes, training IDs,
provenance, means/ranges/domain. Never use full-FIT C2 in development or refit it.
Missing parent => CROSS_FIT_PARENT_NOT_AVAILABLE, synthetic work only.
Predeclare each fold's source/geometry common support for all arms/lambdas.
Nonfinite/failed/unqualified predictions do not drop rows; candidate unselectable.
Select per-family lambda by mean held-design mean-shot mass-weighted RMSE mg/g;
within 1e-6 mg/g of minimum prefer larger lambda. These diagnostics inherit a
previously selected parent family/lambda; not unbiased nested validation.
Then fit each selected family once (three starts) and S0 once on eligible FIT,
using exact immutable final C2. Planned 549 iterative starts and 16 S0 fits.
Hard 600 starts, 8000 actual calls/start, four-hour real computation ceiling,
12 GiB process address-space cap, 5 GiB new private evidence; one worker and one
BLAS thread. Exclusive persistent accounting cannot reset on restart.

Use fixed 64-point Gauss-Legendre quadrature on each knot segment in fits and
queries. Share arms integrate the pointwise PRODUCT; not product of averages.
Qualify every retained held/final interval against 128-point and independent
adaptive quad, split at knots, epsabs=1e-14 kg, epsrel=2e-13, limit=200.
Allowance=max(|I64-I128|,|I64-Iadapt|+err,|I128-Iadapt|+err)
+128*machine_epsilon*(width+abs(I64)); add explicit source-coordinate roundoff.
Ceiling 1e-9 kg caffeine/window, fixed before outcomes; no statistical confidence.
Reuse 006's explicit fraction-3 shared-anchor reconciliation within four ulps,
retaining original coordinates and twice the kg difference in allowance. All
other before-anchor queries, including one ulp, fail. No source geometry repair.

API: immutable strict versioned/hash-bound model and state, condition on early
inputs, predict independent intervals and remaining caffeine to specified mass.
Internally kg beverage/kg caffeine and kg/kg; TDS percent/100, caffeine mg/g/1000;
mg=1e6*integral(q db); mg/g=1000*integral(q db)/width. Units/basis/schema/unknown
features/nonfinite/invalid early masses/reversed/out-of-domain requests fail.
Zero interval gives zero mass, undefined concentration. Feature extrapolation
is flagged as diagnostic. No workbook, target table or optimizer at inference.
S0/S1/S2 import verified parent bytes rather than the installed package fallback.
Serialized D0 contains no TDS inputs or C2 state.

RESEARCH_ONLY / SOURCE_INTERNAL / TARGET_EXPOSED /
RETROSPECTIVE_CAMPAIGN_SEPARATED_CONDITIONAL_PREDICTION.
No fresh blind holdout, external independence, mechanistic identification,
whole-cup/inventory closure, universal transfer or hydraulic prediction.
Modeled unassayed gaps are not directly validated whole-suffix measurements.
Analytical recovery/censoring uncertainty, blank/LOD/LOQ remain unestablished.
PHYSICAL_VALIDATION=NOT_ESTABLISHED. Pannusch/Schmieder Mendeley
10.17632/y2tz67f6ry.1; source-derived CC-BY-NC-3.0 separate from software license.
No unrestricted commercial-deployment claim.
