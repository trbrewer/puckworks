# One-calibration-shot source adaptation

SCI-MD-MASS-DELIVERY-008. G1 / NO_GOVERNING_PHYSICS_CHANGE.
Written before implementation and real fitting. Fixed primary A2. Research
artifacts only; no production registration, default or dependency-lock change.

F2 references unchanged accepted 007 C2 predictions on identical inputs and
coordinates. A2 and A0 are new immutable wrappers around the accepted 006 C2
and C0 respectively: q(b)=sigmoid(eta_parent(b,z)+delta_j). Parent theta,
features, centering, scales, knots, domain, rights and State remain unchanged.
C0 target state accepts only m1,m2; C2 additionally accepts q1,q2. No target
suffix value, total or source dictionary is an input to either state.

For calibration shot j solve sum_k integral_[a_k,b_k] q(b) db =
sum_k d_k*q_observed,k over that shot's observed declared suffix windows only.
This is one aggregate logit level correction, not an inventory, assay bias,
rate, mass-clock correction or physical parameter. Apply the identical scalar
to every other eligible shot. No diagonal, favourable choice, nearest neighbour,
multi-shot fit, prediction averaging, rescue arm or target-specific optimization.

Use unchanged parent IntervalGeometry and stable knot-split sigmoid integration;
never midpoint assays or a fabricated parent State with altered derived logits.
Zero offset delegates to the parent operator. Brent bracket [-20,20], xtol=1e-12,
rtol=4*binary64 epsilon, maxiter=200. No root gives CALIBRATION_RANGE_FAILURE.
Certify independent mass-sign bounds at root +/- first successful radius in
[1e-10,1e-9,1e-8,1e-7,1e-6], confined to the bracket. Include independent
quadrature/refinement, parent roundoff, mass-coordinate reconciliation and
observed-product/sum roundoff in sign bounds. No certified pair gives
NUMERICAL_ENCLOSURE_UNRESOLVED. The enclosure radius propagated to an interval
is max(delta-lo,hi-delta)*(end-start)/4. Add integration and explicit coordinate
conversion allowances. These are numerical allowances, not confidence intervals.

M is a task-local fit of the unchanged GRUDEVA-CLOCK-001 MASS kernel:
q(b)=c0*exp(-(a_m*b_g)^p), b_g=1000*b_kg, a_t=exactly zero.
It consumes the same single calibration shot's same positive-mass suffix
observations, with no pretrained coefficients or target chemistry. Objective:
sum d_k*(100*S_hat_k/d_k-TDS_observed_percent_k)^2 / sum d_k.
Its SI interface converts kg to g before the inherited kernel, g solute to kg
afterwards. Independent adaptive quadrature and 128/256-order refinement qualify
each prediction, including SI conversion roundoff. Optimization convergence is
not parameter identifiability or physical validation.

Inherited bounds: c0=[0,1], a_m=[0,10] per gram, p=[0.25,4]. Exactly these eight
starts in order (c0,a_m,p): (0.2,0.03,1), (0.3,0.08,1), (0.1,0.02,0.5),
(0.5,0.1,2), (0.25,0.05,4), (0.4,0.15,0.25), (0.15,0,1), (0.75,0.3,3).
SciPy least_squares: method=trf, jac=2-point, diff_step=1e-6,
ftol=xtol=gtol=1e-10, x_scale=[0.2,0.05,1], max_nfev=2000,
tr_solver=exact, loss=linear. An actual residual-call counter includes numerical
Jacobians and refuses call 2001. Retain every start, last/final coefficients,
termination, actual calls, nfev/njev, boundary hits (distance <=1e-7), elapsed time
and selection. Lowest converged objective wins; exact ties retain start order.
All-start failure retains an unsupported model/fold.

All arms retain the 006 domain ceiling 0.06971540000000001 kg and the same
target windows/anchor. For M this is a comparison envelope. Flag coordinates
outside its own calibration-shot suffix mass range; do not exclude them.
Parent feature-extrapolation flags are separate. Finite nonnegative solute must
not exceed interval beverage mass within its numerical allowance, and the total
allowance must be <=1e-9 kg. Preserve rejection of wrong units, before-anchor,
unknown/reversed/nonfinite and out-of-domain queries. Zero-width solute is zero,
concentration undefined. Conservation/additivity and independent batch ordering
are required. No clipping, widened domains, new starts or enlarged tolerances.

Strict immutable artifact/state serialization binds schema, units, parent model
canonical identity, source identity, calibrator identity and calibration-record
identity. Unknown/duplicate fields and altered derived fields are rejected.
Fitting, prediction, score and saved-result report are distinct operations.

A2 versus M compares practical utility at the same ONE-calibration-shot budget,
not equal architecture inputs. A0 is the chemistry-ablation control, not a
specific second-assay ablation: C1 is absent.

RESEARCH_ONLY; TARGET_EXPOSED;
RETROSPECTIVE_ONE_CALIBRATION_SHOT_SOURCE_ADAPTATION;
CONDITIONAL_ON_COLLECTED_BEVERAGE_MASS_AND_PERMITTED_EARLY_CHEMISTRY;
PHYSICAL_VALIDATION=NOT_ESTABLISHED. No zero-shot transfer, fresh blind or
prospective validation, two-physical-assay demonstration, real-time policy,
universal portability, hydraulics, inventory closure, identified measurement
bias or physical mechanism. Source shots vary; arbitrary block order does not
establish chronology or a controlled fixed-recipe calibration campaign.
Pannusch/Schmieder derived artifacts retain CC-BY-NC-3.0 (Mendeley
10.17632/y2tz67f6ry.1), separately from software licensing and the existing
Grudeva PERMISSION_DOCUMENTED scope; no new rights grant or raw redistribution.
