# SCI-MD-MASS-DELIVERY-001

Puckworks issue #277; EWP issue #183.

G1; NO_GOVERNING_PHYSICS_CHANGE. Research only. Owner task authorizes one
implementation, training calibration, independent pre-score audit, frozen
TARGET_EXPOSED / SOURCE_INTERNAL campaign evaluation, and open unmerged PRs.
No production registration/default/lock changes, native runs, inventory mapping,
laboratory work, mechanistic refits, or successor.

## Task selection and source preflight

New information: absolute fraction TDS and delivered-solids transfer of the
Grudeva-supported model family to source-specific Pannusch calibration; previous
Pannusch empirical comparisons used normalized shares. Positive: retain a useful
conditional research output component. Negative: reject its declared predictive
use, keeping software and scientific fitness separate. Blocked: identify the
specific source/support/numerical limitation without inventing a rescue task.
Grinder-to-cup link: reusable output conditional on beverage mass, not hydraulics.
Repeated inventory/flow blockers are not reopened: direct mass-basis regression
needs neither inlet histories nor initial inventory. Existing qualified fraction
records and complete collection arrays provide the lower-cost route.

Bases: Puckworks 85442cbc6341a872a90769ba5217ca3f375b4c2a /
3fddf9dca7543a1229ef71192cf2d71defde4b83; EWP
9b11bafddb2e64c1b5af7c64026d8a5910dee0b7 /
ab59c6b2ab3b44ab8ab32feac17eb9f3627a2e64. Verified live merged predecessors
Puckworks #276 and EWP #182; producer f395dc004a34f00d8e4583e62d5c22f066198d9f
and its identical tree above. Historical code/data/results remain unchanged.

FIT_2021_12 experiments 9,10,11,14,15 at source grind 1.7: five conditions,
15 shots, 90 TDS fractions. PRED-C01,C02,C05,C06: primary 12 shots/72 fractions.
PRED-C03,C04: temperature-ramp stress 6/36. PRED-C07,C08: flow-ramp stress 6/36.
Physical shots are indivisible. No other grind, experiment 46, or March chemistry
enters fitting, basis selection, normalization, domain or threshold selection.

Use existing source-input, experiment, grind, exclusion and fraction registers;
resolve the external corpus through existing configuration. Reuse reconstruction
MAT loading and assay indices (1,2,3,5,7,10). Use each run's qualified mE_cum,
including every intervening vial. Verify against full mE and source workbook
net weights; a missing required measured prefix fails the affected source contract.
Reuse source tE: FIT mean-mass-rate reconstruction; PRED previously qualified
quadratic reconstruction. These are source-fitted collection clocks, not measured
hydraulic histories. Origin is zero collected beverage at the source collection
origin, without wetting or first-drip inventions. March vial 11 lies after the last
assay and remains unassayed collected mass in coverage accounting.

Observed solute kg = measured beverage kg * percent TDS /100. Cross-check the
8-decimal source export's derived mg using rounding propagated from mass, TDS and
mg fields (not experimental uncertainty). HPLC spills do not exclude valid TDS.
Duplicate identical analytical rows collapse by physical shot/fraction/analyte;
conflicting duplicates fail. Missing chemistry remains missing. Per-shot assayed
support totals never become measured whole-cup totals. Raw and row-level evidence
remain private. Pannusch/Schmieder source DOI 10.17632/y2tz67f6ry.1 and derived
coefficients/tables retain CC-BY-NC-3.0 treatment, distinct from first-party code.

## Frozen mathematics and development policy

MASS q(b)=c0 exp(-(kb*b)^p), b kg, q kg/kg, S kg. Bounds c0 [0,1], kb [0,10000]
kg^-1, p [.25,4]. Computational bounds, not physical priors. TIME substitutes
source t seconds and kt [0,10] s^-1. Eight inherited starts from grudeva_clock:
(.2,.03,1),(.3,.08,1),(.1,.02,.5),(.5,.1,2),(.25,.05,4),(.4,.15,.25),
(.15,0,1),(.75,.3,3). MASS multiplies rates and rate x_scale by 1000;
TIME uses original rates. No historical scientific replay or coefficient transfer.
One shared vector, no shot amplitude/offset. No final-mass normalization.

Integrate over measured beverage mass, including TIME. Primary timing inside
an interval is t0+(t1-t0)*u, u=(b-b0)/(b1-b0); sensitivity conventions are u^2
and sqrt(u), separately calibrated on FIT only. Neither midpoint nor endpoint
concentration times mass is the operator. Zero width gives zero mass and undefined
concentration. Invalid inputs and unsupported units/bases fail explicitly.

Prediction support is [0,max training b_end], and TIME additionally requires
[0,max training t_end]. No later-campaign expansion. Out-of-domain records remain
in all accounting with no extrapolated prediction or passing condition claim.
A modeled stop-mass integral is conditional on achieving that mass and predicts
no time/flow/pressure. Modeled gaps remain predictions, never ground truth.

Training residual i = 100*(predicted average q_i - observed q_i)*
sqrt(m_i/(N_conditions*N_shots_in_condition*sum_valid_assayed_mass_of_shot)).
Thus squared norm averages mass-weighted squared pp errors with equal conditions
and equal shots. Positive valid measured support only; empty shots fail.
TRF least_squares, 2-point Jacobian, exact trust solver, linear loss,
ftol=xtol=gtol=1e-10, diff_step=1e-6, scales [.2,50,1] MASS / [.2,.05,1] TIME.
Count initial and all numerical-Jacobian calls; hard 2000 calls/start. Lowest
converged loss, ties by start index; retain failures and final/last parameters.
Expected 6 fits (five LOCO plus final) * 4 treatments (MASS + three TIME) *
8 starts = 192, under 500. No optimizer or family expansion after scores.

BOUNDARY_AWARE_EMPIRICAL: continuous piecewise-linear q, coefficient bounds [0,1],
no monotonicity. Fixed K in {5,9}, lambda in {0,.001,.1,10}. Equally spaced knots
from zero to maximum training mass coordinate. Exact integrated hat bases fit
interval averages. Let x=b/B, h=1/(K-1); penalty=lambda*mean((100*D2(q)/h^2)^2),
in pp^2, matching the residual objective units. Linear bounded least squares,
tolerance 1e-12, max_iter 1000. Training-only LOCO selects smallest mean shot R
(equal conditions), ties within 1e-10 pp by fewer knots then larger penalty.
Fold basis/domain use only that fold's training coordinates. Out-of-domain fold
cases remain explicit; selection reports coverage and cannot masquerade as an
unbiased full-support score. Final fit uses all 15 training shots. Selection
requires a common supported evaluation subset across all eight candidates;
missing support counts are reported, and no adequacy decision uses a reduced
case denominator. This is a development diagnostic, not final validation.

## Numerics, freeze and decisions

128-point transformed Gauss-Legendre u=v^8; refinement 256. Independent adaptive
quadrature directly on u, epsabs=1e-13 kg, epsrel=1e-11, limit=200. Allowance is
max(refinement difference, independent difference + reported error), target
<=1e-9 kg/interval. Piecewise-linear integration is analytic, independently
checked with adaptive quadrature split at knots. Numerical allowances propagate
through triangle inequalities into every metric and decision; threshold boxes
that straddle a gate give NUMERICALLY_UNRESOLVED. Not measurement uncertainty.

Freeze source/split/implementation/test hashes, fitted models, hyperparameters,
metrics and all primary/secondary predictions before the independent audit and
single later-campaign scoring. The author cannot approve the audit. Every target
row is joined only by intact interval identity at scoring. Source-internal and
already exposed targets are never described as newly blind.

Shot R = sqrt(sum(m*e_pp^2)/sum(m)); B = 100*sum(pred-observed)/sum(m).
Report interval solute RMSE g, signed/absolute assayed-total error g, maximum
absolute running residual over the ordered assayed sequence, support and numerical
bounds. Average shot metrics within condition, then conditions equally.
Adequacy requires each primary condition's mean R<=1.00 pp and mean abs(B)<=.50 pp,
qualified numerics and complete eligible support. Working budgets only.
MASS competitive requires primary adequacy and R/mean abs(B) <= baseline +.10 pp.
Material gain, separately vs TIME and empirical: >=20% and >=.10 pp R reduction,
lower R in >=3/4 primary conditions, abs(B) deterioration <=.10 pp.

Fixed 2000 paired hierarchical bootstrap draws (PCG64 seed 20260926): resample
conditions, then shots within each selected condition; intact fraction vectors
and candidate pairing retained. 2.5/97.5 percentiles are descriptive with four
conditions, not population/equivalence claims. Ramps reported separately and
cannot rescue primary failure. All shots/conditions remain in the report.

PHYSICAL_VALIDATION=NOT_ESTABLISHED. No whole-pull hydraulic capability,
c_s0/inventory/absolute-closure resolution, identified residual inventory,
disentangled coffee/roast/campaign cause, universal coefficients or measured
chemistry across gaps. No automatic successor. Both PRs stay OPEN/UNMERGED.
