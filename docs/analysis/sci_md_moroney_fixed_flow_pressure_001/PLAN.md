# SCI-MD-MORONEY-FIXED-FLOW-PRESSURE-001

Recorded 2026-10-26 before new extraction/calculation.
G1 / NO_GOVERNING_PHYSICS_CHANGE / RESEARCH_ONLY / RETROSPECTIVE /
TARGET_EXPOSED / SOURCE_INTERNAL / NONSCORING.
PHYSICAL_VALIDATION=NOT_ESTABLISHED.

## Question, value and exposure

At the reported common flow and coffee loading, how different are Figure 12's
native 9.0-bar and 2.3-bar concentration profiles at the same beverage mass,
and which fixed-mass signs survive a declared graphical-reading allowance?
New information is Figure 12 source qualification and fixed-mass contrasts,
not another endpoint-matrix/restart-pressure analysis or transport calibration.
Resolved graphical contrasts support source-conditioned observational differences
and limited capability wording. Unresolved signs still quantify differences;
they do not establish equality or practical equivalence. Source qualification
failure produces precise readiness blockers, never qualified numbers from a
four-row deletion of the unaudited CSV. Grinder-to-cup value is separating
reported chemical-output differences from nominal hydraulic throughput changes,
without identifying causality.

The public figure, raw digitization, apparent similarities and suspected legend
contamination are already exposed. This is neither blinded, preregistered, a new
holdout nor independent predictive validation. No protected scorer, model
selection, kinetic fit or new campaign. Existing identity: moroney2015/data.

## State and source-access preflight

Fresh remote Puckworks main and implementation base:
0004749e4e72c9db9c34b653dd4e4f8a1fa128ee (includes #366).
Fresh EWP main: f44c33dbb9b4fb80143e360e6f4a90f8ac0aa516, read-only.
An isolated worktree/branch preserves existing work. Local state, Moroney
branches and open PRs were inspected; no overlapping Figure 12 task found.
Repository rules, onboarding, minimum-necessary governance, development/data
guides, available-data policy, MANIFEST/register, card, accepted transfer records
and Cameron reading plan inform this task. Transfer remains CALIBRATION_INADEQUATE.

Established external-data configuration resolves the owner collection. A primary
PDF there matches accepted SHA256
896672a997e585a50d97f988caa66259a9a8ed0067300ea7d19725a13c01c4a8.
Verify 19 pages, Figure 12 on index 17 / printed 233, section G.3 on 232–233,
section 2.3 and Figure 3. Inspect native objects and independent page renders.
Restricted PDF/renders stay external. No new source equivalence is assumed.
Source qualification is this task's first unit, not a separate review stage.

## Observations and operators

Authenticate JK material, 60 g loading/mass basis, 250 mL/min, native pressure
labels, beverage mass g and concentration mg solubles/g beverage. Keep pot (a)
and exit (b) separate. Preserve Figure 3 differential-pressure versus G.3/Figure 12
absolute-pressure wording unless apparatus evidence actually reconciles it.
No invented conversion, outlet pressure, bed-pressure change or EWP boundary.
Common nominal flow/dose do not establish common bed state or other conditions.
Batch assay calibration/precision do not automatically apply to flow-through data.

Account for all 94 raw rows, all experimental marker candidates including tails,
legends, calibration objects and omitted/ambiguous candidates. Split marker
subpaths; retain stable row, drawing, sequence and subpath IDs, geometry/strokes,
native centers, legacy differences and reasons. Rows 7/32/54/79 are inspection
targets, not a deletion list; 90 observations is only an expectation. Calibrate
from all labelled ticks, never padded frames. Preserve negative tails. Figure 3
reuse receives lineage links, not extra experimental counts or substituted values.
Raw files/predecessors remain byte-identical; legacy loader behavior stays explicit.

Declare piecewise-linear c_L(M), c_H(M) and Delta_c=c_H-c_L in mg/g using all
qualified native coordinates. No rescaling, normalization, smoothing, shifting,
clipping, fitting or extrapolation; unequal grids are never paired by row.
An internal unresolved observation breaks support; confirmed legends do not.
Only authenticated duplicate renderings may collapse; inconsistent equal-x
ordinates remain unsupported. Track panel/connected components and brackets/weights.
Retain all 14 slots: both panels at M=50,100,200,400,600,800,900 g, with nulls
and reasons when unsupported. Central and sensitivity statuses remain separate.

On each common central component, evaluate both interpolants at its endpoints
and every internal knot of either series. Preserve union knots and signed min/max,
absolute max, all tied knots and constant attaining intervals. Difference is affine
between knots: this exactly evaluates the declared representation, not physical
between-observation behavior. Disclose arithmetic precision and rounding.

## Graphical sensitivity and optional derivations

Apply 0.25 PDF point plus half applicable stroke width around admitted center
candidates and calibration ticks; enclose candidate disagreement first and include
calibration residuals. This is researcher-defined graphical sensitivity, not assay
precision, SD, confidence or an experimental uncertainty distribution.
Propagate horizontal and vertical allowances once. Prefer shared panel calibration;
shared vertical offset cancels and scale is applied consistently. A transparent
rectangular outer relaxation may drop coordinate/calibration dependencies; marginal
extrema need not be jointly realizable and are not sharp geometry claims.

Calculate only the 14 slots. Certify universal coverage independently of possible
brackets: for each ordered gap-free component, upper(first x)<=M<=lower(last x)
for both series. Require upper(x_i)<lower(x_i+1); otherwise report method/order
unsupported without narrowing allowances. For every possibly active adjacent
segment, restrict x0<=M<=x1 and use
w_min=(M-min(u0,M))/(u1-min(u0,M)),
w_max=(M-l0)/(max(l1,M)-l0). Evaluate endpoint ordinate bounds at both weights,
enclose all brackets, then enclose H-L (or valid shared-calibration equivalent).
Preserve nominal inclusion. Classify POSITIVE if lower>0, NEGATIVE if upper<0,
SIGN_UNRESOLVED if zero included, UNSUPPORTED otherwise; use protected internal
arithmetic and outward display rounding. No continuous uncertainty ribbon.

Absolute mg/g differences are primary. Ratios are omitted unless useful and the
whole low-pressure denominator interval is positive; no floors. Enable optional
Delta_S=M*Delta_c_pot in mg only if the same cumulative-mass denominator is
authenticated for both conditions, considering mixing/withdrawals/reconstruction.
Otherwise retain unsupported derivation and concentration results. M is the fixed
analysis target, not a second uncertainty. Never integrate from an unseen origin.

## Verification and delivery

Focused tests cover object accounting/subpaths/lineage, calibration/signed tails,
unequal grids/exact knots/gaps/duplicates, analytic crossings/constant extrema,
horizontal and vertical perturbations/alternate brackets/universal coverage/order,
shared calibration or explicit outer relaxation, zero/outward rounding, optional
derivation gates, deterministic offline regeneration and preservation hashes.
Independently recompute actual extrema. One independent reviewer inspects actual
source objects/semantics, representative arithmetic and all central extrema/claims;
record access and outcome honestly, pending if unavailable. Run affected tests,
static checks, generators and repository merge requirements; keep scientific,
software and hosted CI results separate. Reuse unchanged checks after corrections.

Deliver qualified records, source/object notes, contrasts/union knots/results,
one comparison figure with VizSpec, identities/reproduction/verification/review
receipts and narrow active-authority updates in one OPEN/DRAFT/UNMERGED PR,
auto-merge disabled. No model/framework/production API, EWP write, dependency-pin
or lock change, release, laboratory work, author contact, merge or successor.
No causal pressure effect, statistical significance, equality, equivalence or
universal pressure independence follows. Retain drip-filter/source-material limits.
