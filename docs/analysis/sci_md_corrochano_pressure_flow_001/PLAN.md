# SCI-MD-CORROCHANO-PRESSURE-FLOW-001 — frozen reading plan

G1 / NO_GOVERNING_PHYSICS_CHANGE / RESEARCH_ONLY / RETROSPECTIVE /
TARGET_EXPOSED / SOURCE_INTERNAL / PHYSICAL_VALIDATION=NOT_ESTABLISHED.

This plan is frozen before coordinate transcription or numerical scoring.
Source inspection, the owner's qualitative description, and viewing the two
native panels preceded the plan. This is neither prospective nor blinded.
The task is an observation intake and conditional compatibility study, with no
hydraulic fit, mechanism implementation, new property campaign or successor.

Intake main identities: Puckworks 96d8fe8779f065f12eeeed3c96de0a2d0c4a758b;
read-only EWP aace2cc6b6c2a393d2dbfb0274104192ca6c7203. Both match live main.
Isolated branch research/sci-md-corrochano-pressure-flow-001. No equivalent
intake found in current tree, local task branches or relevant GitHub PR search.
The configured external collection is mounted. The existing inventory's eleven
Corrochano CSVs were opened and rehashed; they are older tables/fit summaries,
not authenticated Figure 6.23 paired records. A held exact-hash thesis is
available. This bounded check is not a corpus census or a raw-data absence claim.

Source: Roman Corrochano (2017), Birmingham Eng.D., Figure 6.23, printed p.266 /
PDF p.291. PDF SHA256 f131d9893e2ac78ce0664d5528beac4be51a02cf1ae684e41920fbc6cadc8818.
Actual embedded 512×384 JPEGs: flow object3223 SHA256
9812ced032ea7a8a4a3a2ab24c5d0fcfcdbd6599356042d8b327e07d00788c9b;
pressure object3226 SHA256
9ce1ffc678791654b61c1966ca98ede419dbc5b2dbf88ab9032ebdd997234240.
PyMuPDF 2.0 extracted them by inspecting the actual page image list. Source
PDF/images/overlays remain external. Inspect pp.62–65,86–88,250–258,266–267,274;
pp.231–232 reconcile the cold-method temperature. Figures6.15/6.16 are context,
6.24 continues one cold trace, and3.3 supplies calibration provenance only.

## Frozen recovery and uncertainty rules

Score Figure6.23 only: PRIMARY 10,20,30,40,50,60 seconds; SECONDARY
5,15,25,35,45,55 seconds. Keep grids separate; no pooled-grid decision.
No shifted times or extra scored brews. The primary grid avoids earliest startup
but does not certify completed wetting/storage/thermal transients.

Use native pixel coordinates, top-left origin, increasing x right/y down.
Calibrate both panels from labelled extreme axis anchors with ±1 native pixel
shared anchor uncertainty; check internal ticks. For each nominal time use the
union of its inverse-affine x positions under those anchor bounds, expanded by
2 native pixels on each side. Enclose all retained ordinate ink over that full
horizontal band, including visible spikes, stroke width and grid obstruction;
expand its y extrema by 2 native pixels. Convert by all affine corners, using
existing affine_enclosure. These conservative reading bounds are not instrument
error, replicate uncertainty, confidence intervals or a probabilistic model.
Do not reduce guards to obtain a witness. Record full pixel enclosures before
guards and resulting time enclosures. Central estimates remain null for envelopes
or ambiguous strokes. At a plotted indication floor truncate negative reading
bounds to zero and flag censoring; no exact physical zero or detection threshold.

Use condition-wide envelopes as the primary recovery. Retain an individual
within-panel fragment only if its stroke can be followed continuously through
all claimed times without an unresolved crossing/overlap. A separated fragment
may end and a new fragment begin; do not join them by rank. Record requested
slots, visible count lower bounds, UNKNOWN totals where needed, overlaps,
endpoints and complete-versus-subset coverage. Every coloured stroke must be
accounted for at a universal witness. If a complete band extends beyond a visible
endpoint, that slot is unsupported; do not clip it into a new scored time.
Occlusion may be conservatively enclosed only when its enclosing range is
source-supported; otherwise mark ambiguity/incomplete support explicitly.

Colour is a condition label (blue=cold15°C, red=hot80°C), supported by the
surrounding lower-cold-resistance description and blue cold continuation6.24.
Caption dashes are not a coloured run key. Use Psi_B and initial400kg/m³;
preserve the generic20°C versus figure-specific15°C discrepancy. Do not import
steady-state hydration/preparation into the first-minute observer.

## Frozen comparisons and quantifiers

Compute inlet-referenced apparent conductance G_app=Q_meter/P_bed_reported,
Q in m³/s, P in Pa, G in m³/(Pa s). For nonnegative Q and P_L>0 use the outer
rectangle [Q_L/P_U,Q_U/P_L]. Missing, censored, nonpositive-denominator and
unbounded dispositions remain explicit JSON null/status values. Use the reported
pressure ordinates; never apply apparatus correction twice or reconstruct Ptrans.
Record the printed Figure3.3 polynomial/curve discrepancy without repair or fit.
Classify flow support against the displayed calibration observations, with
endpoint-reading ambiguity; the axis range is not calibration support. No
invented calibration-error bound or calibration-temperature assumption.

Authenticated run pairs take precedence if found. Otherwise enumerate every
fixed cross-panel permutation only when both panels have defensible persistent
individual tracks (three each imply six). Never switch partners across time.
Within-panel ambiguity is separate. Where identity is unresolved use complete
condition envelopes, not a fictitious permutation count. For a defensible flow
fragment without a pressure identity, its ratio to the *entire condition pressure
envelope* is an explicitly labelled outer bound for every possible pressure
partner; any conclusion remains restricted to that fragment and the assumed
same-condition panel population. Do not count it as an authenticated physical run.

Reuse closure(), compatibility(), affine_enclosure() from the unchanged Melrose
module. Assess nondecreasing, nonincreasing and constant intervals using every
transitively ordered pair. Assess decline followed by recovery through the SAME
intermediate reading with consistent coverage. Record strongest witnesses and
all numerical comparisons. Strict separation only; touching is not a change.
Independently check strict decisions with exact rational arithmetic from the
committed coordinates/anchors, retaining rational margins for witnesses.

Rectangles relax shared calibration, common displayed time, identity, fixed
pairing, and flow-dependent pressure correction. Infeasibility excludes all
contained admissible readings; feasibility is only not-excluded by that
relaxation, without a checked joint witness. Envelope exclusions carry complete
condition-envelope quantifiers at named times, never fabricated trend counts.
Keep subset, one pairing, every pairing, every run and at-least-one-run claims
distinct. No matched cold/hot brews, sample independence or significance claims.

At each supported grid time compute cold-minus-hot interval differences and
cold/hot interval ratios (positive hot lower bound required for finite upper
ratio). Retain unbounded/unsupported/instrument-limited cases. These are
condition-group comparisons. Under the hypothetical single-phase quasi-static
Darcy/common-geometry observer, mu_hot/mu_cold=(alpha_hot/alpha_cold)*(G_c/G_h),
alpha=Q_meter/Q_bed. Report G_c/G_h as a required viscosity ratio only for an
explicit EQUAL-alpha scenario. Unknown alpha leaves physical viscosity unresolved.
Do not transplant Figure6.20, repair its printed viscosity unit, or use its
inferred other-condition history as a synchronized measured bound.

## Interpretation, verification and completion

Separate A published-indication changes; B pairing/coverage/calibration/observer
qualifications; C conditional compatibility with a fixed-topology passive positive-
linear quasi-static network and time-invariant proportional observer; D physical
validation NOT_ESTABLISHED. Every edge conductance nondecreasing implies effective
K nondecreasing along a run; constant imposed P is unnecessary for Q/P. This is
not a cross-run/pressure theorem or a general nonlinear/dynamic claim. A decline
constrains the conjunction, not its cause. A feasible rectangle validates nothing.
Preserve PR348, EWP UNRESOLVED_BOUNDED_ANALYSIS, line-pressure NOT_ASSESSED, and
shared campaign identity. State exactly what the new pressure trace improves.

Produce committed native coordinates/contracts/coverage, normalized readings,
full numerical results, original reconstruction plot without bridging gaps, an
offline producer, RESULT.md/JSON, narrow loader/card/manifest/availability-owner
updates and necessary regenerated projections. No runtime/lock/schema framework
changes. Focused checks include SI/calibration/ratios, missingness/censoring,
coverage, fixed pairing/partner switching, within-panel identity, quantified
matching examples, transitive/touching order, same-trough identity, alpha identity,
and deterministic reproduction. Reuse independent finite-order checks with
HiGHS threads=1. Run normal applicable local QA and live required hosted checks.

Obtain ONE independent substantive scientific review including direct source
coordinate rechecks and strongest numerical witnesses; fix material defects in
this lane. Complete even with unresolved hot trends, pairing, coverage or physical
mapping. No requirement to resolve physical decline or reject viscosity-only.
Deliver one draft PR, open/unmerged, auto-merge disabled, with actual base/head
and truthful revision-specific verification. No successor or merge.
