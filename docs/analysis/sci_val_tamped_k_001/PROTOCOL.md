# SCI-VAL-TAMPED-K-001 frozen comparison contract

G1 / NO_GOVERNING_PHYSICS_CHANGE / RESEARCH_ONLY.
TARGET_EXPOSED_RETROSPECTIVE_COMPARISON. This is not an unseen holdout.

Does source-qualified consolidated packing make the fixed Wadsworth predictor
adequate as a coarse offline prior for this Roman-Corrochano campaign? Gate
decisions and the three-test selection rationale are in GATES.json. A pass
retains only this source-domain composite prior; a failure rejects its all-case
adequacy; an unresolved result retains the exact input/coverage limitation.
None authorizes adoption, new physics, calibration, or a successor.

## Inputs and tested object

**DECLARED-ADAPTER COMPARISON**, explicitly permitted by the task brief.
Native-input semantics are not established: dry laser-diffraction Sauter diameter
is not the arithmetic mean grain diameter, and bed bulk porosity is not a
measurement of connected intergranular porosity. Test the fixed composite
`R = d[3,2]/2; phi_p = epsilon_ss` with no sphericity multiplier or inferred
connectivity. These are declared proxies, not established equalities. No mapping
is selected using permeability agreement. Neither outcome isolates the native
constitutive law independently of this adapter.

The primary campaign is Roman Corrochano et al., J. Food Eng. 150 (2015) 106–116,
DOI 10.1016/j.jfoodeng.2014.11.006. The 2017 thesis is supplementary evidence from
the same campaign, not another sample. The original journal PDF was downloaded
from the University of Birmingham OAI endpoint identified in GATES.json. SHA-256:
`fc5a41225359993da86a7ef3504ea6bbdf2be99811f266e20e55e4156d914d5e`.
The original PDF/rasters remain outside Git. Its printed p.106 explicitly states
CC BY 3.0; the existing journal MANIFEST row's 4.0 label is corrected locally.
The new source-derived input artifact is CC-BY-3.0 with this attribution.

Preserve the full denominator: grind A/B/C/D × initial nominal bulk density
360/400/480 kg/m³, twelve mean-level cases in grind-then-density order. Table 2
on printed p.113 was visually checked against the existing
`puckworks/data/romancorrochano2015/table2.csv`; retain that single target source
and its existing loader. Means and SDs summarize triplicate beds; raw individual
beds are not available here. These are fully extracted steady consolidated beds
(600 s pretreatment), not fresh-shot transients.

Table 1, printed p.109: A/B/C/D d[3,2] = 79.73/101.60/112.86/131.36 µm,
dry air dispersion, laser diffraction, three sample summaries. Convert µm to m
by 1e-6, then diameter to proxy radius by 1/2. Use half the last printed decimal,
0.005 µm, for reading/rounding bounds. Its reported experimental SD is not a
radius bound or confidence interval.

Use **Figure 13 directly** for consolidated central porosity and reading bounds.
Its caption (printed p.115; PDF page 11) defines circles/squares/downward triangles
as 360/400/480 kg/m³. The original figure is raster XObject 380, 886×709 pixels;
there is no vector representation of its markers. Retain twelve pixel centers in
the input JSON, with y=9 at epsilon=0.45 and y=615 at epsilon=0.05. Linear axis
mapping gives each central value. Conservative reading uncertainty: ±5 pixels
per marker (including outline/triangle anchor and overlap ambiguity), ±0.5 pixels
per axis anchor. Evaluate all corner mappings for the porosity bounds. This
resolution is based on the original marker extent, not residuals. X positions
and Table 1 identify grinds without permeability. No global porosity range is
assigned to individual cases.

Figure 6b (printed p.111; PDF page 7, XObject 264) and equations 6a/6b/9 provide
a separate reading consistency check in SOURCE_CONSISTENCY.json, not additional
observations or a selectable reconstruction. Source equations use
rho_particle = 1337*(1-0.53) kg/m³ and
epsilon_ss = (epsilon_initial-lambda_average)/(1-lambda_average).
Figure 13 remains the sole primary reconstruction even if another source
representation would predict permeability better.

Diagnostic arm: use epsilon_initial = 1-rho_bulk/[rho_solid*(1-epsilon_particle)]
with source adopted central rho_solid=1337 kg/m³ and epsilon_particle=0.53.
Use rounding intervals [1336.5,1337.5] and [0.525,0.535], with the same nominal
density keys, radius mapping, alpha and exponent as the primary arm. Evaluate
endpoint extrema of this mapping. This diagnoses the consequence of substituting
consolidated porosity; it is never a selectable alternative to the primary arm.

Bounds quantify recovery of published inputs, not experimental uncertainty,
adapter error, population variability, or confidence. Figure 13's SD error bars
are not used as confidence bounds. Its shared density/particle assumptions are
already part of the published constructed input; do not propagate those again
through the primary Figure 13 readings. Radius is shared within grind; initial
packing constants are shared across all cases. Conservative rectangular bounds
do not define a joint probability distribution or independent replicates.

## Frozen model, numerics, and decision

Import the unchanged `puckworks.models.wadsworth2026.permeability.k_percolation`.
Implementation SHA-256:
`8b4ecd5195d5c35ccb7d5c879cf984a7ff4389ccd61e67f38a667cb2997f9758`.
Fixed defaults: alpha=4808 m⁻¹ and b=4.4. No equation rewrite in the analysis
module, optimization, fitting, learned correction, scaling, or rescue model.
The completed Vaca comparison is context only; no new pooled score or dedicated
rerun. No added Kozeny–Carman or target-calibrated constant comparator.

Inputs must be finite with R>0 and 0<phi<1, ordered bounds containing the central
value, unique and complete case keys, and explicit qualification. Reject missing,
invalid or unsupported inputs rather than clamping or dropping them. Targets and
their rounding bounds must be positive. Prediction functions require no targets.
Output serialization is deterministic JSON with NaN/Infinity forbidden.

For fixed positive alpha/b, d(log k)/d(phi)=b/phi+1/(1-phi)>0 and
d(log k)/d(R)=2/R-2*alpha. Evaluate the radius endpoints and R=1/alpha if inside
the interval, at both porosity endpoints, using the imported model function.
Use these analytic rectangular extrema, not Monte Carlo or an assumed global
radius monotonicity. Software qualification uses synthetic unit conversion,
domain, completeness, independent numerical reference, monotonicity, stationary
point, classification, target separation, and serialization/report tests.
Numerical tests use relative tolerance 1e-12 against independent synthetic values;
IEEE float64 evaluation is sufficient at these bounded source inputs. Numerical
qualification is not physical validation.

No controlling accuracy budget for this exact operational claim was found.
Freeze a **NEW permissive engineering screening criterion**: every one of the
twelve primary predictions must lie within a factor of two of its published mean.
It is not a publication uncertainty limit or an espresso-performance tolerance.
For each target use half its last printed significant decimal as its target
rounding interval, derived from the retained CSV token. Let
q_low=k_low/K_high and q_high=k_high/K_low.

- PASS if q_low>=0.5 and q_high<=2.0.
- FAIL if q_high<0.5 or q_low>2.0.
- Otherwise UNRESOLVED_AT_DECLARED_INPUT_PRECISION.

Full-scope PASS requires twelve qualified case passes. Any definite failure
fails the all-case screen, with incomplete coverage separately stated if present.
No difficult case may be dropped. Each retained arm reports K mean/SD, central
prediction and bounds, central ratio and bounds, signed natural-log ratio, and
qualification flags. SD is descriptive only. Secondary summaries, never replacement
criteria: geometric mean ratio, exp(sqrt(mean(log(ratio)^2))), maximum multiplicative
error, per-grind summaries, and consolidated/initial prediction effects.
This is conditional mean-level adjudication, not a population inference.

## Execution and limits

Protocol and inputs are frozen before implementation through the retained
preimplementation hash receipt. After synthetic tests, serialize target-free
predictions. Bind exact protocol, implementation, model, inputs, targets, tests
and predictions in FREEZE.json. Obtain one genuinely separate pre-scoring audit
using the repository's existing independent agent review mechanism; preserve its
identity and exact reviewed tree. If unavailable, stop PREPARED_AWAITING_INDEPENDENT_REVIEW.
Only then execute one retained comparison. Human RESULT.md generation must consume
retained result JSON without predictions or scoring. Preserve any invalidated
attempt; no silent replacement, refit, mapping switch, tolerance change or case drop.

Scientific dispositions: CONSOLIDATED_INPUT_PRIOR_PASSES_DECLARED_SCREEN,
CONSOLIDATED_INPUT_PRIOR_FAILS_DECLARED_SCREEN,
UNRESOLVED_AT_DECLARED_INPUT_PRECISION, or NOT_ADJUDICATED_INPUT_OR_COVERAGE_BLOCK.
Report baseline/software, gates, adequacy, coverage, review and publication separately.
No EWP edit, dependency/default change, production registration/adoption, native
OpenFOAM, laboratory work, author contact, merge, push, hosted issue/PR, or automatic
successor. No validation of fresh-shot hydraulics, H1, equilibrium, extraction
kinetics or EWP. No screen-resistance reopening or inferred structural mechanism.
EWP's existing lack of qualified permeability transfer remains unchanged.
