# Two-assay amplitude and decay: research model card

SCI-MD-MASS-DELIVERY-005. G1 / NO_GOVERNING_PHYSICS_CHANGE.
Written before implementation or extracting this task's conditioning values.

For beverage mass b (kg), q=A exp(-(k b)^p) (kg/kg),
S(u,v)=integral_u^v q db (kg), TDS=100 S/(v-u) (mass percent).
Reuse exact 001 MASS p0=0.8327267294693588 and domain
[0,0.06350639999999999] kg from its hash-bound artifact. Never refit either.
A is a concentration scale, not initial soluble inventory; k is an effective
mass-coordinate decay parameter, not diffusivity, permeability or physical kinetics.
Computational bounds are 0<=k<=10000 kg^-1 and 0<=A<=1.

Let b_ref=0.01 kg, lambda=(k b_ref)^p, x=(b/b_ref)^p and
F_j(lambda)=mean_j exp(-lambda x) over the measured interval of width m_j.
Solve F2/F1=q2/q1, then A=q1/F1. Integrate intervals, preserving the original
collection origin; never fit midpoint concentrations or reset b at either assay.
For ordered nonoverlapping positive-width intervals, x is strictly increasing
for p>0. d log(F2/F1)/d lambda=E_1,lambda[x]-E_2,lambda[x]<0:
all interior x values in interval 2 exceed those in interval 1, even for touching
endpoints (zero-measure shared boundary). Positive tilted measures preserve this
strict ordering. The ratio is continuous, equals one at zero and decreases
strictly; an admissible bracket therefore has a unique root. Finite k ceiling
can prevent a bracket. A's physical bound is checked separately.

Exact equality q1=q2>0 gives k=0. q1=q2=0 determines zero delivery but leaves
k unidentified (serialize k/lambda as null). Positive q2 with q1=0, q2>q1,
or q2=0<q1 is scientifically incompatible with finite decreasing delivery.
No clipping, epsilon denominator, negative k, invented assay tolerance,
least-squares rescue, grid-minimum selection or scientific bounds expansion.

Exactly six arms, machine labels distinct from AXIS_* decision labels:

- TWO_ASSAY_MASS: local A,k; p=p0 (primary).
- TWO_ASSAY_EXPONENTIAL: local A,k; p=1 (comparator only).
- TWO_ASSAY_FIXED_MASS: frozen MASS; one local alpha from both assays.
- TWO_ASSAY_FIXED_EMPIRICAL: exact 001 empirical knots/values, including its
  nonmonotonicity; one local alpha from both assays.
- SECOND_ASSAY_EMPIRICAL: same empirical curve, alpha=q2/g2.
- FIRST_ASSAY_EMPIRICAL: unchanged 003 fraction-1 operator; same later windows.

For two-assay fixed shapes, alpha=sum(m_j g_j q_j)/sum(m_j g_j^2), the unique
mass-weighted least-squares amplitude when the positive denominator qualifies.
No model chooser, recipe coefficient, dose normalization, third assay, other
anchor pair, varying p, mixtures, shrinkage, smoothing or persistence arm.
All arms require physical concentration bounds and the identical frozen mask.
A failed arm retains every intended slot and cannot reduce a metric denominator.

Numerical contract: deterministic bracketed bisection in lambda, atol=rtol=1e-12,
100 iterations maximum, using inherited transformed 128-point Gauss-Legendre
integration. Exactly one tighter qualification solve (atol=rtol=1e-14, max 100)
uses independent adaptive quadrature; p=1 uses the stable analytic exponential
integral exp(-k a)*[-expm1(-k m)]/k with exact k=0. 256-point quadrature
refinement is also checked. Reference normalized-integral quadrature epsabs=1e-14,
epsrel=2e-13, limit=200; all integral allowances include roundoff and reference
error estimates. These are qualified numerical allowances, not rigorous interval
arithmetic or assay error bars.

Enclose inversion uncertainty using both solve brackets, their discrepancy and
8 times ratio numerical allowance divided by the local absolute ratio slope,
plus roundoff. Verify the resulting endpoints against independent integral
ratio bounds; inability to certify this enclosure is NUMERICALLY_UNRESOLVED,
without another solve or larger scientific bracket. Propagate this interval
through monotone F1 to A bounds and jointly bound future A*I by the product of
positive A and integral bounds (conservatively ignoring their covariance).
Require relative conditioning integral/denominator allowance<=1e-6 and every
final solute allowance<=1e-9 kg. Solver termination alone does not qualify output.
Analytical amplitudes use numerator/denominator interval bounds. FIRST retains
its exact legacy arithmetic/allowances. Preserve failed attempts and counts.

Jacobian for (q1,q2) against (A,lambda) has rows [F_j,A F'_j],
F'_j=-mean_j x exp(-lambda x). det=A F1 F2*(E1[x]-E2[x]) is nonzero for A>0.
Report this Jacobian, its condition number, and the (A,k) Jacobian when regular:
d lambda/dk=p*b_ref*(k*b_ref)^(p-1). At k=0 report the nonregular rate-coordinate
boundary separately; at A=0 report singular unidentified rate. For future average
Fh, d(TDS_h)/d(TDS_1,TDS_2)=[Fh,A Fh'] J^-1 in pp/pp. Fixed-shape sensitivities
follow the analytical amplitude formula; FIRST equals its legacy amplification
and zero second-input derivative. Verify sensitivities by synthetic finite
differences. Invertible local mathematics does not identify physical kinetics.

Typed immutable observations require fractions exactly 1 and 2, common shot,
source, rights and input role, mass kg and mass-basis TDS percent, ordered
nonoverlapping positive widths. Future coordinate-only queries start after
fraction 2 completion and end within the frozen domain. Zero-width queries give
S=0, TDS=null. Strict state loading recomputes and checks all derived fields,
base bytes and transitive first-party runtime hashes; stale/forged states fail.

SOURCE_INTERNAL / TARGET_EXPOSED /
RETROSPECTIVE_TWO_ASSAY_CONDITIONED_COMPARISON. Numerical error, source export
rounding, documented assay uncertainty (no per-assay SD supplied), and between-shot
variability remain separate. No confidence intervals invented. No claim of blind
validation, measurement robustness, real-time assay feasibility, physical kinetic
identification, recipe-to-hydraulics prediction or measured whole-cup totals.
Source-derived material: Pannusch/Schmieder, Mendeley 10.17632/y2tz67f6ry.1,
CC-BY-NC-3.0, separate from first-party software licensing.
